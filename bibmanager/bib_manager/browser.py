# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = [
    'browse',
]

from asyncio import Future, ensure_future
from contextlib import redirect_stdout
import io
import itertools
import os
import re
import textwrap
import webbrowser


from prompt_toolkit import print_formatted_text, search
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import PathCompleter, WordCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import PygmentsTokens, FormattedText
from prompt_toolkit.formatted_text.utils import fragment_list_to_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_bindings import merge_key_bindings
from prompt_toolkit.key_binding.bindings.auto_suggest import \
    load_auto_suggest_bindings
from prompt_toolkit.key_binding.bindings.scroll import (
    scroll_half_page_down,
    scroll_half_page_up,
)
from prompt_toolkit.layout.containers import (
    Float, FloatContainer,
    HSplit, VSplit,
    Window, WindowAlign, ConditionalContainer,
)
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.processors import (
    Transformation,
    Processor,
    AppendAutoSuggestion,
)
from prompt_toolkit.layout.utils import explode_text_fragments
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.selection import PasteMode
from prompt_toolkit.styles import Style, style_from_pygments_cls, merge_styles
from prompt_toolkit.widgets import (
    Button, Dialog, Label, SearchToolbar, TextArea,)
import pygments
from pygments.lexers.bibtex import BibTeXLexer


from . import bib_manager as bm
from .. import config_manager as cm
from .. import pdf_manager as pm
from .. import utils as u
from ..__init__ import __version__ as ver


help_message = f"""\
h       Show this message
enter   Select/unselect entry for saving
s       Save selected entries to file or screen output
f,/,?   Find literal string in the main text
e       Expand/collapse content of current entry
E       Expand/collapse all entries
o       Open PDF of entry (ask to fetch if needed)
b       Open entry in ADS through the web browser
k       Search entries by keywords (authors/years/tags/etc),
          displaying only matching entries
K       Clear keyword-search selection
q       Quit

Navigation
Arrow keys  Move up, down, left, and right
g/G         Go to first/last line
u/d         Scroll up/down
n/N         Go to next/previous search occurrence

This is bibmanager version {ver}
Created by Patricio Cubillos."""

class TextInputDialog:
    """Hello, this is doc"""
    def __init__(self, title="", label_text="", completer=None):
        self.future = Future()

        def accept_text(buf):
            buf.complete_state = None
            self.future.set_result(self.text_area.text)
            if self.text_area.text == "":
                get_app().exit()

        self.text_area = TextArea(
            completer=completer,
            multiline=False,
            width=D(preferred=40),
            accept_handler=accept_text,
        )

        self.dialog = Dialog(
            title=title,
            body=HSplit([
                Label(text=label_text), self.text_area, Label(text="")]),
            width=D(preferred=75),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


class MessageDialog:
    def __init__(self, title, text, asking=False):
        self.future = Future()

        def set_done():
            self.future.set_result(None)
        def accept():
            self.future.set_result(True)
        def cancel():
            self.future.set_result(False)

        if asking:
            buttons = [
                Button(text="Yes", handler=accept),
                Button(text="No", handler=cancel),
            ]
        else:
            buttons = [Button(text="OK", handler=set_done)]

        text = "\n".join([
            textwrap.fill(line, width=71)
            for line in text.splitlines()
            ])
        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=text)]),
            buttons=buttons,
            width=D(preferred=75),
            modal=True,
            )

    def __pt_container__(self):
        return self.dialog


def show_message(title, text):
    async def coroutine():
        dialog = MessageDialog(title, text)
        await show_dialog_as_float(dialog)

    ensure_future(coroutine())


async def show_dialog_as_float(dialog):
    """Coroutine."""
    app = get_app()
    root_container = app.layout.container
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    app.layout.current_window.dialog = dialog
    result = await dialog.future
    if hasattr(app.layout.current_window, 'dialog'):
        del(app.layout.current_window.dialog)
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result


class HighlightEntryProcessor(Processor):
    """Processor to highlight a list of texts in the document."""
    match_fragment = " class:search "
    selected_entries = []

    def toggle_selected_entry(self, entry_key):
        """Select/deselect entry_key from the list of highlighted texts."""
        if entry_key in self.selected_entries:
            self.selected_entries.remove(entry_key)
        else:
            self.selected_entries.append(entry_key)

    def apply_transformation(self, transformation_input):
        (
            buffer_control,
            document,
            lineno,
            source_to_display,
            fragments,
            _,
            _,
        ) = transformation_input.unpack()

        if self.selected_entries and not get_app().is_done:
            # For each search match, replace the style string.
            line_text = fragment_list_to_text(fragments)
            fragments = explode_text_fragments(fragments)

            pattern = "|".join(re.escape(key) for key in self.selected_entries)
            matches = re.finditer(pattern, line_text, flags=re.RegexFlag(0))

            for match in matches:
                for i in range(match.start(), match.end()):
                    old_fragment, text, *_ = fragments[i]
                    fragments[i] = (
                        old_fragment + self.match_fragment,
                        fragments[i][1],
                    )

        return Transformation(fragments)


def get_current_key(doc, keys, get_start_end=False, get_expanded=False):
    """
    Get the key for the bibtex entry currently under the cursor.
    """
    position = doc.cursor_position
    if doc.current_line in keys:
        is_expanded = False
        key = doc.current_line
        if get_start_end:
            start_pos = position + doc.get_start_of_line_position()
            end_pos = position + doc.get_end_of_line_position()
    else:
        is_expanded = True
        start_pos = position + doc.start_of_paragraph()
        end_pos = position + doc.end_of_paragraph()
        # Cursor is in between entries:
        if doc.current_line == '':
            row = doc.cursor_position_row
            # If prev line is key take lower entry, else take upper entry:
            if doc.lines[row-1] in keys:
                start_pos = position + 1
            else:
                end_pos = position - 1
        # Get the key:
        start_bib = doc.text.find('@', start_pos)
        key_start = doc.text.find('{', start_bib)
        key_end = doc.text.find(',', start_bib)
        key = doc.text[key_start+1:key_end].strip()

    if not (get_start_end or get_expanded):
        return key

    output = [key]
    if get_start_end:
        output.append([start_pos, end_pos])
    if get_expanded:
        output.append(is_expanded)
    return tuple(output)


def browse():
    """
    A browser for the bibmanager database.
    """
    # Content of the text buffer:
    bibs = bm.load()
    keys = [bib.key for bib in bibs]
    all_compact_text = "\n".join(keys)
    all_expanded_text = "\n\n".join(bib.meta() + bib.content for bib in bibs)
    # A list object, since I want this to be a global variable
    selected_content = [None]

    lex_style = style_from_pygments_cls(
        pygments.styles.get_style_by_name(cm.get('style')))
    custom_style = Style.from_dict({
        "status": "reverse",
        "status.position": "#aaaa00",
        "status.key": "#ffaa00",
        "shadow": "bg:#440044",
        "not-searching": "#888888",
        })
    style = merge_styles([lex_style, custom_style])

    def get_menubar_text():
        return [
            ("class:status", " ("),
            ("class:status.key", "enter"),
            ("class:status", ")select entry  ("),
            ("class:status.key", "e"),
            ("class:status", ")xpand entry  ("),
            ("class:status.key", "f"),
            ("class:status", ")ind  ("),
            ("class:status.key", "s"),
            ("class:status", ")ave  ("),
            ("class:status.key", "h"),
            ("class:status", ")elp  ("),
            ("class:status.key", "q"),
            ("class:status", ")uit"),
        ]


    def get_menubar_right_text():
        """Get index of entry under cursor."""
        key = get_current_key(text_field.buffer.document, keys)
        return f" {keys.index(key) + 1} "


    def get_infobar_text():
        """Get author-year-title of entry under cursor."""
        key = get_current_key(text_field.buffer.document, keys)
        bib = bibs[keys.index(key)]
        year = '' if bib.year is None else bib.year
        title = 'NO_TITLE' if bib.title is None else bib.title
        return f"{bib.get_authors('ushort')}{year}: {title}"

    search_buffer = Buffer(
        completer=WordCompleter(keys),
        complete_while_typing=False,
        multiline=False)
    literal_search_field = SearchToolbar(
        search_buffer=search_buffer,
        forward_search_prompt = "Text search: ",
        backward_search_prompt = "Text search backward: ",
        ignore_case=False)

    # Entry search bar:
    authors_list = [bib.authors for bib in bibs]
    firsts = sorted(set([
        u.get_authors([authors[0]], format='ushort')
        for authors in authors_list
        if authors is not None]))
    firsts = [
        '^{'+first+'}' if ' ' in first else '^'+first
        for first in firsts]

    lasts = sorted(set([
        u.get_authors([author], format='ushort')
        for authors in authors_list if authors is not None
        for author in authors]))
    lasts = [
        '{'+last+'}' if ' ' in last else last
        for last in lasts]

    bibkeys = [bib.key for bib in bibs]
    bibcodes = [bib.bibcode for bib in bibs if bib.bibcode is not None]
    bibyears = sorted(set([
        str(bib.year) for bib in bibs if bib.year is not None]))
    titles = [bib.title for bib in bibs]
    tags = sorted(set(itertools.chain(
        *[bib.tags for bib in bibs if bib.tags is not None])))

    key_words = {
        'author:"^"': firsts,
        'author:""': lasts,
        'year:': bibyears,
        'title:""': titles,
        'key:': bibkeys,
        'bibcode:': bibcodes,
        'tags:': tags,
    }
    completer = u.DynamicKeywordCompleter(key_words)
    suggester = u.DynamicKeywordSuggester()
    auto_suggest_bindings = load_auto_suggest_bindings()

    # Searcher:
    entry_search_buffer = Buffer(
        completer=completer,
        complete_while_typing=False,
        auto_suggest=suggester,
    )

    def get_line_prefix(lineno, wrap_count):
        return FormattedText([('bold', 'Entry search: '),])
    entry_search_field = Window(
        BufferControl(
            buffer=entry_search_buffer,
            input_processors=[AppendAutoSuggestion()],
        ),
        get_line_prefix=get_line_prefix,
        height=1)
    # Wrap in conditional container to display it only when focused:
    entry_search_focus = Condition(
        lambda: get_app().layout.current_window == entry_search_field)
    entry_search_container = ConditionalContainer(
        content=entry_search_field,
        filter=entry_search_focus,
    )

    text_field = TextArea(
        text=all_compact_text,
        lexer=PygmentsLexer(BibTeXLexer),
        scrollbar=True,
        line_numbers=False,
        read_only=True,
        search_field=literal_search_field,
        input_processors=[HighlightEntryProcessor()],
    )
    text_field.buffer.name = 'text_area_buffer'
    text_field.is_expanded = False
    text_field.compact_text = all_compact_text
    text_field.expanded_text = all_expanded_text
    # Shortcut to HighlightEntryProcessor:
    for processor in text_field.control.input_processors:
        if processor.__class__.__name__ == 'HighlightEntryProcessor':
            text_field.bm_processor = processor
    # Do not highlight searched text:
    sp = text_field.control.default_input_processors[0]
    sp._classname = ' '
    sp._classname_current = ' '

    menu_bar = VSplit([
        Window(
            FormattedTextControl(get_menubar_text),
            style="class:status"),
        Window(
            FormattedTextControl(get_menubar_right_text),
            style="class:status.right",
            width=9,
            align=WindowAlign.RIGHT),
        ],
        height=1,
    )

    info_bar = ConditionalContainer(
        content=Window(
            content=FormattedTextControl(get_infobar_text),
            height=D.exact(1),
            style="class:status",
        ),
        filter=~entry_search_focus,
    )

    body = HSplit([
        menu_bar,
        text_field,
        literal_search_field,
        entry_search_container,
        info_bar,
    ])

    root_container = FloatContainer(
        content=body,
        floats=[
            Float(
                xcursor=True,
                ycursor=True,
                content=CompletionsMenu(max_height=16, scroll_offset=1),
            ),
        ],
    )


    # Key bindings:
    bindings = KeyBindings()

    text_focus = Condition(
        lambda: get_app().layout.current_window == text_field.window)
    dialog_focus = Condition(
        lambda: hasattr(get_app().layout.current_window, 'dialog'))

    @bindings.add("q", filter=text_focus)
    def _quit(event):
        event.app.exit()

    # Navigation:
    @bindings.add("g", filter=text_focus)
    def _go_to_first_line(event):
        event.current_buffer.cursor_position = 0

    @bindings.add("G", filter=text_focus)
    def _go_to_last_line(event) -> None:
        event.current_buffer.cursor_position = len(event.current_buffer.text)

    @bindings.add("d", filter=text_focus)
    def _scroll_down(event):
        scroll_half_page_down(event)

    @bindings.add("u", filter=text_focus)
    def _scroll_up(event):
        scroll_half_page_up(event)

    @bindings.add("n", filter=text_focus)
    def _find_next(event):
        search_state = event.app.current_search_state
        event.current_buffer.apply_search(
            search_state, include_current_position=False, count=event.arg)

    @bindings.add("N", filter=text_focus)
    def _find_previous(event):
        search_state = event.app.current_search_state
        event.current_buffer.apply_search(
            ~search_state, include_current_position=False, count=event.arg)


    @bindings.add("h", filter=text_focus)
    def _show_help(event):
        show_message("Shortcuts", help_message)


    @bindings.add("f", filter=text_focus)
    def _start_literal_search(event):
        search.start_search(direction=search.SearchDirection.FORWARD)


    # TBD: Remove 't' binding no before 17/12/2022
    @bindings.add("t", filter=text_focus)
    @bindings.add("k", filter=text_focus)
    def _start_entry_search(event):
        text_field.current_key = get_current_key(
            event.current_buffer.document, keys)
        event.app.layout.focus(entry_search_field)


    @bindings.add("b", filter=text_focus)
    def _open_in_browser(event):
        key = get_current_key(event.current_buffer.document, keys)
        bib = bm.find(key=key, bibs=bibs)
        if bib.adsurl is not None:
            webbrowser.open(bib.adsurl, new=2)
        else:
            show_message("Message", f"Entry '{key}' does not have an ADS url.")


    @bindings.add("c-c", filter=dialog_focus)
    def _close_dialog(event):
        get_app().layout.current_window.dialog.future.set_result(None)


    @bindings.add("s", filter=text_focus)
    def _save_selected_to_file(event):
        selected = text_field.bm_processor.selected_entries
        if len(selected) == 0:
            show_message("Message", "Nothing to save.")
            return

        async def coroutine():
            dialog = TextInputDialog(
                title="Save to File",
                label_text="\nEnter a file path or leave blank to quit "
                    "and print to screen:\n(press Control-c to cancel)\n",
                completer=PathCompleter(),
            )
            path = await show_dialog_as_float(dialog)
            content = '\n\n'.join(
                bibs[keys.index(key)].content for key in selected)
            if path == "":
                selected_content[0] = content
                # The program termination is in TextInputDialog() since I
                # need to close this coroutine first.
                return
            if path is not None:
                try:
                    with open(path, "w") as f:
                        f.write(content)
                except IOError as e:
                    show_message("Error", str(e))

        ensure_future(coroutine())


    @bindings.add("enter", filter=text_focus)
    def _toggle_selected_entry(event):
        "Select/deselect entry pointed by the cursor."
        key = get_current_key(event.current_buffer.document, keys)
        text_field.bm_processor.toggle_selected_entry(key)


    @bindings.add("enter", filter=entry_search_focus)
    def _select_entries(event):
        "Parse the input tag text and send focus back to main text."
        # Reset tag text to '':
        doc = event.current_buffer.document
        start_pos = doc.cursor_position + doc.get_start_of_line_position()
        event.current_buffer.cursor_position = start_pos
        event.current_buffer.delete(
            doc.get_end_of_line_position() - doc.get_start_of_line_position())

        # Catch text and parse search text:
        matches = u.parse_search(doc.current_line)
        if len(matches) == 0:
            text_field.compact_text = all_compact_text[:]
            text_field.expanded_text = all_expanded_text[:]
            search_buffer.completer.words = keys
        else:
            text_field.compact_text = "\n".join([bib.key for bib in matches])
            text_field.expanded_text = "\n\n".join(
                bib.meta() + bib.content for bib in matches)
            search_buffer.completer.words = [bib.key for bib in matches]

        # Return focus to main text:
        event.app.layout.focus(text_field.window)

        # Update main text with selected tag:
        buffer = event.current_buffer
        text_field.text = text_field.compact_text
        if text_field.current_key in search_buffer.completer.words:
            buffer_position = text_field.text.index(text_field.current_key)
        else:
            buffer_position = 0
        buffer.cursor_position = buffer_position
        text_field.is_expanded = False

    # TBD: Remove 'T' binding no before 17/12/2022
    @bindings.add("T", filter=text_focus)
    @bindings.add("K", filter=text_focus)
    def _deselect_tags(event):
        buffer = event.current_buffer
        key = get_current_key(buffer.document, keys)
        text_field.compact_text = all_compact_text[:]
        text_field.expanded_text = all_expanded_text[:]
        search_buffer.completer.words = keys
        # Update main text:
        text_field.text = text_field.compact_text
        buffer.cursor_position = buffer.text.index(key)
        text_field.is_expanded = False


    @bindings.add("e", filter=text_focus)
    def _expand_collapse_entry(event):
        "Expand/collapse current entry."
        doc = event.current_buffer.document
        key, start_end, is_expanded = get_current_key(
            doc, keys, get_start_end=True, get_expanded=True)
        bib = bm.find(key=key, bibs=bibs)
        if is_expanded:
            # Remove blank lines around if surrounded by keys:
            start_row, _ = doc._find_line_start_index(start_end[0])
            if start_row > 0 and doc.lines[start_row-2] in keys:
                start_end[0] -= 1
            end_row, _ = doc._find_line_start_index(start_end[1])
            if end_row < doc.line_count-1 and doc.lines[end_row+2] in keys:
                start_end[1] += 1
            event.app.clipboard.set_text(bib.key)
        else:
            expanded_content = bib.meta() + bib.content
            row = doc.cursor_position_row
            # Add blank lines around if surrounded by keys:
            if row > 0 and doc.lines[row-1] != '':
                expanded_content = '\n' + expanded_content
            if row < doc.line_count-1 and doc.lines[row+1] != '':
                expanded_content = expanded_content + '\n'
            event.app.clipboard.set_text(expanded_content)

        text_field.read_only = False
        event.current_buffer.cursor_position = start_end[0]
        event.current_buffer.delete(count=start_end[1] - start_end[0])
        event.current_buffer.paste_clipboard_data(
            event.app.clipboard.get_data(), count=event.arg,
            paste_mode=PasteMode.VI_BEFORE)
        text_field.read_only = True
        if is_expanded:
            event.current_buffer.cursor_position = start_end[0]


    @bindings.add("E", filter=text_focus)
    def _expand_collapse_all(event):
        "Expand/collapse all entries."
        buffer = event.current_buffer
        key = get_current_key(buffer.document, keys)
        if text_field.is_expanded:
            text_field.text = text_field.compact_text
        else:
            text_field.text = text_field.expanded_text

        buffer.cursor_position = buffer.text.index(key)
        text_field.is_expanded = not text_field.is_expanded


    @bindings.add("o", filter=text_focus)
    def _open_pdf(event):
        buffer = event.current_buffer
        key = get_current_key(buffer.document, keys)
        bib = bm.find(key=key, bibs=bibs)

        has_pdf = bib.pdf is not None
        has_bibcode = bib.bibcode is not None
        is_missing = has_pdf and not os.path.exists(f'{u.BM_PDF()}{bib.pdf}')

        if not has_pdf and not has_bibcode:
            show_message("Message",
                f"BibTeX entry '{key}' does not have a PDF.")
            return

        if has_pdf and not is_missing:
            pm.open(key=key)
            return

        if has_pdf and is_missing and not has_bibcode:
            show_message("Message",
                f"BibTeX entry has a PDF file: {bib.pdf}, but the file "
                 "could not be found.")
            return

        # Need to fetch before opening:
        async def coroutine():
            dialog = MessageDialog(
                "PDF file not found",
                "Fetch from ADS?\n(might take a few seconds ...)",
                asking=True)
            fetch = await show_dialog_as_float(dialog)
            if fetch:
                with io.StringIO() as buf, redirect_stdout(buf):
                    fetched = pm.fetch(bib.bibcode, replace=True)
                    fetch_output = buf.getvalue()

                if fetched is None:
                    show_message("PDF fetch failed", fetch_output)
                else:
                    show_message("PDF fetch succeeded.", fetch_output)
                    pm.open(key=key)
        ensure_future(coroutine())

    key_bindings = merge_key_bindings([
        auto_suggest_bindings,
        bindings,
    ])
    application = Application(
        layout=Layout(root_container, focused_element=text_field),
        key_bindings=key_bindings,
        enable_page_navigation_bindings=True,
        style=style,
        full_screen=True,
    )

    application.run()
    if selected_content[0] is not None:
        tokens = list(pygments.lex(selected_content[0], lexer=BibTeXLexer()))

        print_formatted_text(
            PygmentsTokens(tokens),
            end="",
            style=lex_style,
            #output=create_output(sys.stdout),
            )

