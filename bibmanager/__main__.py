# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import re
import argparse
import textwrap
from datetime import date
from packaging import version

import prompt_toolkit
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter

from . import bib_manager    as bm
from . import latex_manager  as lm
from . import config_manager as cm
from . import ads_manager    as am
from . import pdf_manager    as pm
from . import utils as u
from .__init__ import __version__


# Parser Main Documentation:
main_description = f"""
BibTeX Database Management:
---------------------------
  reset       Reset the bibmanager database.
  merge       Merge a BibTeX file into the bibmanager database.
  edit        Edit the bibmanager database in a text editor.
  add         Add entries into the bibmanager database.
  search      Search entries in the bibmanager database.
  browse      Browse through the bibmanager database.
  export      Export the bibmanager database into a bib file.
  cleanup     Clean up a bibtex file of duplicates and outdated entries.
  config      Manage the bibmanager configuration parameters.

LaTeX Management:
-----------------
  bibtex      Generate a BibTeX file from a LaTeX file.
  latex       Compile a LaTeX file with the latex command.
  pdflatex    Compile a LaTeX file with the pdflatex command.

ADS Management:
---------------
  ads-search  Do a query on ADS.
  ads-add     Add entries from ADS by bibcode into the bibmanager database.
  ads-update  Update bibmanager database cross-checking entries with ADS.

PDF Management:
---------------
  fetch       Fetch a PDF file from ADS.
  open        Open the PDF file of a BibTex entry in the database.
  pdf         Link a PDF file to a BibTex entry in the database.

For additional details on a specific command, see 'bibm command -h'.
See the full bibmanager docs at https://bibmanager.readthedocs.io

Copyright (c) 2018-{date.today().year} Patricio Cubillos and contributors.
bibmanager is open-source software under the MIT license, see:
https://pcubillos.github.io/bibmanager/license.html
"""


def cli_reset(args):
    """Command-line interface for reset call."""
    if not args.database and not args.config:
      args.database = True
      args.config   = True

    if args.database:
        if args.bibfile is not None and not os.path.exists(args.bibfile):
            print(f"\nError: Input BibTeX file '{args.bibfile}' does not "
                   "exist.")
            return
        if args.bibfile is not None:
            bibzero = f" with BibTeX file: '{args.bibfile}'."
            args.bibfile = os.path.realpath(args.bibfile)
        else:
            bibzero = "."
        print(f"Initializing new bibmanager database{bibzero}")
    if args.config:
        print("Resetting config parameters.")
    bm.init(args.bibfile, args.database, args.config)


def cli_merge(args):
    """Command-line interface for merge call."""
    if args.bibfile is not None and not os.path.exists(args.bibfile):
        print(f"\nError: Input BibTeX file '{args.bibfile}' does not exist.")
        return
    if args.bibfile is not None:
        args.bibfile = os.path.realpath(args.bibfile)
    bm.merge(bibfile=args.bibfile, take=args.take)
    print(f"\nMerged BibTeX file '{args.bibfile}' into bibmanager database.")


def cli_edit(args):
    """Command-line interface for edit call."""
    bm.edit()


def cli_add(args):
    """Command-line interface for add call."""
    bm.add_entries(take=args.take)


def cli_search(args):
    """Command-line interface for search call."""
    bibs = bm.load()
    completer = u.KeyWordCompleter(u.search_keywords, bibs)
    suggester = u.AutoSuggestKeyCompleter()
    validator = u.AlwaysPassValidator(bibs,
        "(Press 'tab' for autocomplete)")

    session = prompt_toolkit.PromptSession(
        history=FileHistory(u.BM_HISTORY_SEARCH()))
    inputs = session.prompt(
        "(Press 'tab' for autocomplete)\n",
        auto_suggest=suggester,
        completer=completer,
        complete_while_typing=False,
        validator=validator,
        validate_while_typing=True,
        bottom_toolbar=validator.bottom_toolbar)

    # Parse inputs:
    authors  = re.findall(r'author:"([^"]+)', inputs)
    title_kw = re.findall(r'title:"([^"]+)', inputs)
    years    = re.search(r'year:[\s]*([^\s]+)', inputs)
    key      = re.findall(r'key:[\s]*([^\s]+)', inputs)
    bibcode  = re.findall(r'bibcode:[\s]*([^\s]+)', inputs)
    if years is not None:
        years = years.group(1)
    if len(key) == 0:
        key = None
    if len(bibcode) == 0:
        bibcode = None

    # Cast year string to integer or list of integers:
    if years is None:
        pass
    elif len(years) == 4 and years.isnumeric():
        years = int(years)
    elif len(years) == 5 and years.startswith('-') and years[1:].isnumeric():
        years = [0, int(years[1:])]
    elif len(years) == 5 and years.endswith('-') and years[0:4].isnumeric():
        years = [int(years[0:4]), 9999]
    elif len(years) == 9 and years[0:4].isnumeric() and years[5:].isnumeric():
        years = [int(years[0:4]), int(years[5:9])]
    else:
        print(f"\nInvalid format for input year: {years}")
        return

    if (len(authors) == 0 and len(title_kw) == 0
        and years is None and key is None and bibcode is None):
        return
    matches = bm.search(authors, years, title_kw, key, bibcode)

    # Display outputs depending on the verb level:
    if args.verb >= 3:
        bm.display_bibs(labels=None, bibs=matches, meta=True)
        return

    for match in matches:
        year = '' if match.year is None else f', {match.year}'
        title = textwrap.fill(
            f"Title: {match.title}{year}",
            width=78, subsequent_indent='       ')
        author_format = 'short' if args.verb < 2 else 'long'
        authors = textwrap.fill(
            f"Authors: {match.get_authors(format=author_format)}",
            width=78, subsequent_indent='         ')
        keys = f"\nkey: {match.key}"
        if args.verb > 0 and match.pdf is not None:
            keys = f"\nPDF file:  {match.pdf}{keys}"
        if args.verb > 0 and match.eprint is not None:
            keys = f"\narXiv url: http://arxiv.org/abs/{match.eprint}{keys}"
        if args.verb > 0 and match.adsurl is not None:
            keys = f"\nADS url:   {match.adsurl}{keys}"
            keys = f"\nbibcode:   {match.bibcode}{keys}"
        print(f"\n{title}\n{authors}{keys}")


def cli_browse(args):
    """Command-line interface for database browser."""
    bm.browse()


def cli_export(args):
    """Command-line interface for export call."""
    path, bibfile = os.path.split(os.path.realpath(args.bibfile))
    if not os.path.exists(path):
        print(f"\nError: Output dir does not exists: '{path}'")
        return
    bibfile, extension = os.path.splitext(bibfile)
    if extension == ".bib":
        bm.export(bm.load(), bibfile=args.bibfile, meta=args.meta)
    elif extension == ".bbl":
        print("\nSorry, export to .bbl output is not implemented yet.")
        return
    else:
        print(f"\nError: Invalid file extension ('{extension}'), must be "
               "'.bib' or '.bbl'.")


def cli_cleanup(args):
    """Command-line interface to clean up a bibfile."""
    bibs = bm.read_file(args.bibfile)
    if args.ads:
        try:
            updated = am.update(base=bibs)
            bibs = updated
        except ValueError as e:
            print(f"\nError: {str(e)}. Continue without ADS update.")
    bm.export(bibs, args.bibfile)


def cli_config(args):
    """Command-line interface for config call."""
    try:
        if args.param is None:
            cm.display()
        elif args.value is None:
            cm.help(args.param)
        else:
            cm.set(args.param, args.value)
    except ValueError as e:
        print(f"\nError: {str(e)}")


def cli_bibtex(args):
    """Command-line interface for bibtex call."""
    lm.build_bib(args.texfile, args.bibfile)

def cli_latex(args):
    """Command-line interface for latex call."""
    try:
        lm.compile_latex(args.texfile, args.paper)
    except ValueError as e:
        print(f"\nError: {str(e)}")


def cli_pdflatex(args):
    """Command-line interface for pdflatex call."""
    try:
        lm.compile_pdflatex(args.texfile)
    except ValueError as e:
        print(f"\nError: {str(e)}")


def cli_ads_search(args):
    """Command-line interface for ads-search call."""
    if args.next:
        query = None
    else:
        completer = u.KeyWordCompleter(u.ads_keywords, bm.load())
        session = prompt_toolkit.PromptSession(
            history=FileHistory(u.BM_HISTORY_ADS()))
        query = session.prompt(
            "(Press 'tab' for autocomplete)\n",
            auto_suggest=u.AutoSuggestCompleter(),
            completer=completer,
            complete_while_typing=False,
            ).strip()
        if query == "" and os.path.exists(u.BM_CACHE()):
            query = None
        elif query == "":
            return
    try:
        am.manager(query)
    except ValueError as e:
        print(f"\nError: {str(e)}")

    args.bibcode = None
    args.key = None
    if args.add:
        print("\nAdd entry from ADS:")
        cli_ads_add(args)
    elif args.fetch or args.open:
        print("\nFetch/open entry from ADS:")
        args.keycode = None
        args.filename = None
        cli_fetch(args)


def cli_ads_add(args):
    """Command-line interface for ads-add call."""
    if args.bibcode is None and args.key is None:
        inputs = prompt_toolkit.prompt(
            "Enter pairs of ADS bibcodes and BibTeX keys, one pair per line\n"
            "separated by blanks (press META+ENTER or ESCAPE ENTER when "
            "done):\n", multiline=True)
        bibcodes, keys = [], []
        inputs = inputs.strip().split('\n')
        for line in inputs:
            if len(line.split()) == 0:
                continue
            elif len(line.split()) != 2:
                print("\nError: Invalid syntax, each line must have two strings"
                      " specifying a bibcode\n and key, separated by a blank.")
                return
            bibcode, key = line.split()
            bibcodes.append(bibcode)
            keys.append(key)

    elif args.bibcode is not None and args.key is not None:
        bibcodes = [args.bibcode]
        keys     = [args.key]
    else:
        print("\nError: Invalid input, 'bibm ads-add' expects either zero or "
              "two arguments.")
        return
    try:
        am.add_bibtex(bibcodes, keys)
    except ValueError as e:
        print(f"\nError: {str(e)}")

    if args.fetch or args.open:
        for bibcode in bibcodes:
            args.keycode = bibcode
            args.filename = None
            cli_fetch(args)


def cli_ads_update(args):
    """Command-line interface for ads-update call."""
    update_keys = args.update == 'arxiv'
    try:
        am.update(update_keys=update_keys)
    except ValueError as e:
        print(f"\nError: {str(e)}")


def cli_fetch(args):
    """Command-line interface for ADS PDF-fetch calls."""
    filename = args.filename
    # Fetch without prompt:
    if args.keycode is not None:
        if bm.find(key=args.keycode) is not None:
            key, bibcode = args.keycode, None
        else:
            bibcode, key = args.keycode, None

    else:
        field = 'bibcode'
        prompt_text = ("Syntax is:  key: KEY_VALUE FILENAME\n"
            "       or:  bibcode: BIBCODE_VALUE FILENAME\n"
            "       (FILENAME is optional.  Press 'tab' for autocomplete)\n")
        keywords = 'key bibcode'.split()
        try:
            prompt_input = bm.prompt_search(keywords, field, prompt_text)
        except ValueError as e:
            print(f"\nError: {str(e)}")
            return
        key, bibcode = prompt_input[0]
        filename = prompt_input[1][0]

    bib = bm.find(key=key, bibcode=bibcode)
    if bibcode is not None and bib is None:
        print("")
        filename = pm.fetch(bibcode, filename)
        if args.open and filename is not None:
            pm.open(pdf_file=filename)
        return

    if bib is None:
        print('\nError: BibTex entry is not in Bibmanager database.')
        return
    if bib.bibcode is None:
        print('\nError: BibTex entry is not in ADS database.')
        return

    try:
        pm.fetch(bib.bibcode, filename)
    except ValueError as e:
        print(f"\nError: {str(e)}")

    # Reload BibTex entry:
    bib = bm.find(key=bib.key)
    if bib.pdf is not None and args.open:
        pm.open(key=bib.key)
    elif bib.pdf is not None:
        print(f'\nTo open the PDF file, execute:\nbibm open {bib.key}')


def cli_open(args):
    """Open the PDF file of a BibTex entry from the database."""
    if args.keycode is not None:
        key, bibcode, pdf = None, None, None
        if bm.find(key=args.keycode) is not None:
            key = args.keycode
        elif bm.find(bibcode=args.keycode) is not None:
            bibcode = args.keycode
        elif args.keycode.lower().endswith('.pdf'):
            pdf = args.keycode
        else:
            print('\nError: Input is no key, bibcode, or PDF of any entry '
                'in Bibmanager database')
            return

    if args.keycode is None:
        field = 'pdf'
        prompt_text = ("Syntax is:  key: KEY_VALUE\n"
            "       or:  bibcode: BIBCODE_VALUE\n"
            "       or:  pdf: PDF_VALUE\n"
            "(Press 'tab' for autocomplete)\n")
        keywords = 'key bibcode pdf'.split()
        try:
            prompt_input = bm.prompt_search(keywords, field, prompt_text)
        except ValueError as e:
            print(f"\nError: {str(e)}")
            return
        key, bibcode, pdf = prompt_input[0]

    try:
        pm.open(pdf=pdf, key=key, bibcode=bibcode)
    except ValueError as e:
        print(f"\nError: {str(e)}")
        if pdf is None:
            bib = bm.find(key=key, bibcode=bibcode)
            if bib is not None and bib.bibcode is not None:
                fetch_pdf = u.req_input("Fetch from ADS?\n[]yes [n]o\n",
                    options=['', 'y', 'yes', 'n', 'no'])
                if fetch_pdf in ['', 'y', 'yes']:
                    pm.fetch(bib.bibcode)


def cli_link(args):
    """Command-line interface for setting/linking PDFs to entries."""
    filename = args.filename
    if args.keycode is not None:
        pdf = args.pdf
        if bm.find(key=args.keycode) is not None:
            key, bibcode = args.keycode, None
        else:
            bibcode, key = args.keycode, None

    else:
        field = 'key'  # (i.e., all entries)
        prompt_text = (
            "Syntax is:  key: KEY_VALUE PDF_FILE FILENAME\n"
            "       or:  bibcode: BIBCODE_VALUE PDF_FILE FILENAME\n"
            "(output FILENAME is optional, "
            "set it to guess for automated naming)\n")
        keywords = 'key bibcode'.split()
        try:
            prompt_input = bm.prompt_search(keywords, field, prompt_text)
        except ValueError as e:
            print(f"\nError: {str(e)}")
            return
        key, bibcode = prompt_input[0]

        pdf = prompt_input[1][0]
        if len(prompt_input[1]) > 1:
            filename = prompt_input[1][1]

    # The entry:
    bib = bm.find(key=key, bibcode=bibcode)
    if bib is None:
        print('\nError: BibTex entry is not in Bibmanager database.')
        return
    # The PDF file:
    if pdf is None:
        print('\nError: Path to PDF file is missing.')
        return
    pdf = os.path.expanduser(pdf)
    if not os.path.isfile(pdf):
        print('\nError: input PDF file does not exist.')
        return
    # The filename:
    if filename is None:
        filename = os.path.basename(pdf)
    elif filename == 'guess':
        filename = pm.guess_name(bib)

    try:
        pm.set_pdf(bib, pdf, filename=filename)
    except ValueError as e:
        print(f"\nError: {str(e)}")


def main():
    """
    Bibmanager command-line interface.

    Partially inspired by these:
    - https://stackoverflow.com/questions/7869345/
    - https://stackoverflow.com/questions/32017020/
    """
    # Initialization check:
    if not os.path.exists(u.HOME + 'config'):
        bm.init(bibfile=None)

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-v', '--version', action='version',
        help="Show bibmanager's version.",
        version=f'bibmanager version {__version__}')

    # And now the sub-commands:
    sp = parser.add_subparsers(title="These are the bibmanager commands",
        description=main_description, metavar='command')

    # Database Management:
    reset_description = f"""
{u.BOLD}Reset the bibmanager database.{u.END}

Description
  This command resets the bibmanager database from scratch.
  It creates a .bibmanager/ folder in the user folder (if it does not
  exists already), and it resets the bibmanager configuration to
  its default values.

  If the user provides the 'bibfile' argument, this command will
  populate the database with the entries from that file; otherwise,
  it will set an empty database.

  Note that this will overwrite any pre-existing database.  In
  principle the user should not execute this command more than once
  in a given CPU."""
    reset = sp.add_parser('reset', description=reset_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    reset.add_argument("bibfile", action="store", nargs='?',
        help="Path to an existing BibTeX file.")
    group = reset.add_mutually_exclusive_group()
    group.add_argument('-d', '--database', action='store_true', default=False,
        help="Reset only the bibmanager database.")
    group.add_argument('-c', '--config',   action='store_true', default=False,
        help="Reset only the bibmanager config parameters.")
    reset.set_defaults(func=cli_reset)


    merge_description = f"""
{u.BOLD}Merge a BibTeX file into the bibmanager database.{u.END}

Description
  This command merges the content from an input BibTeX file with the
  bibmanager database.

  The optional 'take' arguments defines the protocol for possible-
  duplicate entries.  Either take the 'old' entry (database), take
  the 'new' entry (bibfile), or 'ask' the user through the prompt
  (displaying the alternatives).  bibmanager considers four fields
  to check for duplicates: doi, isbn, bibcode, and eprint.

  Additionally, bibmanager considers two more cases (always asking):
  (1) new entry has duplicate key but different content, and
  (2) new entry has duplicate title but different key."""
    merge = sp.add_parser('merge', description=merge_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    merge.add_argument("bibfile", action="store",
        help="Path to an existing BibTeX file.")
    merge.add_argument("take", action="store", nargs='?', metavar='take',
        help="Decision protocol for duplicates (choose: {%(choices)s}, "
        "default: %(default)s)", choices=['old','new','ask'], default='old')
    merge.set_defaults(func=cli_merge)


    edit_description = f"""
{u.BOLD}Edit the bibmanager database in a text editor.{u.END}

Description
  This command let's you manually edit the bibmanager database,
  in your pre-defined text editor.  Once finished editing, save and
  close the text editor, and press ENTER in the terminal to
  incorporate the edits (edits after continuing on the terminal won't
  count).

  bibmanager selects the OS default text editor.  But the user can
  set a preferred editor, see 'bibm config -h' for more information."""
    edit = sp.add_parser('edit', description=edit_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    edit.set_defaults(func=cli_edit)


    add_description = f"""
{u.BOLD}Add entries into the bibmanager database.{u.END}

Description
  This command allows the user to manually add BibTeX entries into
  the bibmanager database through the terminal prompt.

  The optional 'take' argument defines the protocol for possible-
  duplicate entries.  Either take the 'old' entry (database), take
  the 'new' entry (bibfile), or 'ask' the user through the prompt
  (displaying the alternatives).  bibmanager considers four fields
  to check for duplicates: doi, isbn, bibcode, and eprint.

  Additionally, bibmanager considers two more cases (always asking):
  (1) new entry has duplicate key but different content, and
  (2) new entry has duplicate title but different key."""
    add = sp.add_parser('add', description=add_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add.add_argument("take", action="store", nargs='?', metavar='take',
        help="Decision protocol for duplicates (choose: {%(choices)s}, "
        "default: %(default)s)", choices=['old','new','ask'], default='new')
    add.set_defaults(func=cli_add)


    search_description = f"""
{u.BOLD}Search entries in the bibmanager database.{u.END}

Description
  This command will trigger a prompt where the user can search for entries
  in the bibmanager database by authors, years, title keywords, BibTeX key,
  or ADS bibcode.  The matching results are displayed on screen according
  to the specified verbosity.
  Search syntax is similar to ADS searches (including tab completion).

  Multiple author, title keyword, and year queries act with AND logic;
  whereas multiple-key queries and multiple-bibcode queries act with OR
  logic (see examples below).

  There are four levels of verbosity (see examples below):
  - zero shows the title, year, first author, and key;
  - one adds the ADS and arXiv urls;
  - two adds the full list of authors;
  - and three displays the full BibTeX entry.

Notes
  (1) There's no need to worry about case in author names, unless they
      conflict with the BibTeX format rules:
      http://mirror.easyname.at/ctan/info/bibtex/tamethebeast/ttb_en.pdf, p.23
  (2) Title keywords searches are case-insensitive.

Examples
  # Search by last name (press tab to prompt the autocompleter):
  bibm search
  author:"oliphant, t"

  # Search by first-author only:
  bibm search
  author:"^oliphant, t"

  # Search multiple authors (using AND logic):
  bibm search
  author:"oliphant, t" author:"jones, e"

  # Search by author, year, and title words/phrases (using AND logic):
  bibm search
  author:"oliphant, t" year:2006 title:"numpy"

  # Search multiple words/phrases in title (using AND logic):
  bibm search
  title:"HD 209458b" title:"atmospheric circulation"

  # Search on specific year:
  bibm search
  author:"cubillos, p" year:2016
  # Search anything between the specified years:
  bibm search
  author:"cubillos, p" year:2014-2016
  # Search anything up to the specified year:
  bibm search
  author:"cubillos, p" year:-2016
  # Search anything since the specified year:
  bibm search
  author:"cubillos, p" year:2016-

  # Search by bibcode:
  bibm search
  bibcode:1917PASP...29..206C

  # Search multiple bibcodes at once (using OR logic):
  bibm search
  bibcode:1917PASP...29..206C bibcode:1918ApJ....48..154S

  # Use '-v' argument to increase verbosity, for example:
  # Display title, year, first author, and all keys/urls:
  bibm search -v
  author:"Burbidge, E"
  # Display title, year, author list, and all keys/urls:
  bibm search -vv
  author:"Burbidge, E"
  # Display full BibTeX entry:
  bibm search -vvv
  author:"Burbidge, E"
"""
    search = sp.add_parser('search', description=search_description,
        usage="bibm search [-h] [-v]",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    search.add_argument('-v', '--verb', action='count', default=0,
        help='Set output verbosity.')
    search.set_defaults(func=cli_search)


    browse_description = f"""
{u.BOLD}Browse through the bibmanager database.{u.END}

Description
  Display the entire bibmanager database into a full-screen application
  that lets you:
  - Navigate through or search for specific entries
  - Visualize the entries' full BibTeX content
  - Select entries for printing to screen or to file
  - Open the entries' PDF files
  - Open the entries in ADS through the web browser

Examples
  bibm browse
"""
    browse = sp.add_parser('browse', description=browse_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    browse.set_defaults(func=cli_browse)


    export_description = f"""
{u.BOLD}Export the bibmanager database into a bib file.{u.END}

Description
  Export the entire bibmanager database into a bibliography file to a
  .bib or .bbl format according to the file extension of the
  'bibfile' argument (TBD: for the moment, only export to .bib)."""
    export = sp.add_parser('export', description=export_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    export.add_argument("bibfile", action="store",
        help="Path to an output BibTeX file.")
    export.add_argument('-meta', action='store_true', default=False,
        help="Also include meta-information in output file.")
    export.set_defaults(func=cli_export)


    cleanup_description = f"""
{u.BOLD}Clean up a bibtex file of duplicates and outdated entries.{u.END}

Description
  'Clean up' a BibTeX file by removing duplicates, sorting the entries,
  and (if requested) updating the entries by cross-checking against
  the ADS database.  All of this is done independently of the bibmanager
  database.

Examples
  # Remove duplicates, update ADS entries, and sort:
  bibm cleanup file.bib -ads
"""
    cleanup = sp.add_parser('cleanup', description=cleanup_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    cleanup.add_argument("bibfile", action="store",
        help="Path to an existing BibTeX file.")
    cleanup.add_argument('-ads', action='store_true', default=False,
        help="Update the bibfile entries cross-checking against the ADS "
             "database.")
    cleanup.set_defaults(func=cli_cleanup)


    config_description = f"""
{u.BOLD}Manage the bibmanager configuration parameters.{u.END}

Description
  This command displays or sets the value of bibmanager config parameters.
  These are the parameters that can be set by the user:
  - style       sets the color-syntax style of displayed BibTeX entries.
  - text_editor sets the text editor for 'bibm edit' calls.
  - paper       sets the default paper format for latex compilation.
  - ads_token   sets the token required for ADS requests.
  - ads_display sets the number of entries to show at once for ADS searches.
  - home        sets the Bibmanager home directory.

  The number of arguments determines the action of this command (see
  examples below):
  - with no arguments, display all available parameters and values.
  - with the 'param' argument, display detailed info on the specified
    parameter and its current value.
  - with both 'param' and 'value' arguments, set the value of the parameter.

Examples
  # Display all config parameters and values:
  bibm config
  # Display value and help for the style parameter:
  bibm config style
  # Set the value of the BibTeX color-syntax:
  bibm config style autumn"""
    config = sp.add_parser('config',  description=config_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    config.add_argument("param", action="store", nargs='?',
        help="A bibmanager config parameter.")
    config.add_argument("value", action="store", nargs='?',
        help="Value for a bibmanager config parameter.")
    config.set_defaults(func=cli_config)


    # Latex Management:
    bibtex_description = f"""
{u.BOLD}Generate a BibTeX file from a LaTeX file.{u.END}

Description
  This command generates a BibTeX file by searching for the citation
  keys in the input LaTeX file, and stores the output into BibTeX file,
  named after the argument in the '\\bibliography{{bib_file}}' call in
  the LaTeX file.  Alternatively, the user can specify the name of the
  output BibTeX file with the 'bibfile' argument.

  Any citation key not found in the bibmanager database, will be
  shown on the screen prompt."""
    bibtex = sp.add_parser('bibtex', description=bibtex_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    bibtex.add_argument("texfile", action="store",
        help="Path to an existing LaTeX file.")
    bibtex.add_argument("bibfile", action="store", nargs='?',
        help="Path to an output BibTeX file.")
    bibtex.set_defaults(func=cli_bibtex)


    latex_description = f"""
{u.BOLD}Compile a LaTeX file using the latex command.{u.END}

Description
  This command compiles a LaTeX file using the latex command,
  executing the following calls:
  - Compute a BibTex file out of the citation calls in the LaTeX file.
  - Remove all outputs from previous compilations.
  - Call latex, bibtex, latex, latex to produce a .dvi file.
  - Call dvi2ps and ps2pdf to produce the final .pdf file.

  Prefer this command over the 'bibm pdflatex' command when the LaTeX
  file contains .ps or .eps figures (as opposed to .pdf, .png, or .jpeg).

  Note that the user does not necessarily need to be in the dir
  where the LaTeX files are."""
    latex = sp.add_parser('latex', description=latex_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    latex.add_argument("texfile", action="store",
        help="Path to an existing LaTeX file.")
    latex.add_argument("paper", action="store", nargs='?',
        help="Paper format, e.g., letter or A4 (default=%(default)s).",
        default=cm.get('paper'))
    latex.set_defaults(func=cli_latex)


    pdflatex_description = f"""
{u.BOLD}Compile a LaTeX file using the pdflatex command.{u.END}

Description
  This command compiles a LaTeX file using the pdflatex command,
  executing the following calls:
  - Compute a BibTeX file out of the citation calls in the LaTeX file.
  - Remove all outputs from previous compilations.
  - Call pdflatex, bibtex, pdflatex, pdflatex to produce a .pdf file.

  Prefer this command over the 'bibm latex' command when the LaTeX file
  contains .pdf, .png, or .jpeg figures (as opposed to .ps or .eps).

  Note that the user does not necessarily need to be in the dir
  where the LaTeX files are."""
    pdflatex = sp.add_parser('pdflatex', description=pdflatex_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    pdflatex.add_argument("texfile", action="store",
        help="Path to an existing LaTeX file.")
    pdflatex.set_defaults(func=cli_pdflatex)


    # ADS Management:
    asearch_description = f"""
{u.BOLD}Do a query on ADS.{u.END}

Description
  This command enables ADS queries.  The query syntax is identical to
  a query in the new ADS's one-box search engine:
  https://ui.adsabs.harvard.edu.
  Here there is a detailed documentations for ADS searches:
  https://adsabs.github.io/help/search/search-syntax
  See below for typical query examples.

  A query will display at most 'ads_display' entries on screen at once
  (see 'bibm config ads_display').  If a query matched more entries,
  the user can execute 'bibm ads-search -n' to display the next set of
  entries.
  Note that per ADS syntax, fields in quotes must use double quotes.

  If you set the -a/--add flag, the code will prompt to add entries to
  the database right after showing the ADS search results.
  Similarly, set the -f/--fetch or -o/--open flags to prompt to fetch
  or open PDF files right after showing the ADS search results.
  Note that you can combine these to add and fetch/open at the same
  time (e.g., bibm ads-search -a -o), or you can fetch/open PDFs that
  are not in the database (e.g., bibm ads-search -o).

Examples
  # Search entries for author (press tab to prompt the autocompleter):
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"^Fortney, J"

  # Display the next set of entries that matched this query:
  bibm ads-search -n

  # Search by author in article:
  bibm ads-search
  author:"Fortney, J"
  # Search by first author:
  bibm ads-search
  author:"^Fortney, J"
  # Search multiple authors:
  bibm ads-search
  author:("Fortney, J" AND "Showman, A")

  # Search by author AND year:
  bibm ads-search
  author:"Fortney, J" year:2010
  # Search by author AND year range:
  bibm ads-search
  author:"Fortney, J" year:2010-2019
  # Search by author AND words/phrases in title:
  bibm ads-search
  author:"Fortney, J" title:Spitzer
  # Search by author AND words/phrases in abstract:
  bibm ads-search
  author:"Fortney, J" abs:"HD 209458b"

  # Search by author AND request only articles:
  bibm ads-search
  author:"Fortney, J" property:article
  # Search by author AND request only peer-reviewed articles:
  bibm ads-search
  author:"Fortney, J" property:refereed"""
    asearch = sp.add_parser('ads-search', description=asearch_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    asearch.add_argument('-n', '--next', action='store_true', default=False,
        help="Display next set of entries that matched the previous query.")
    asearch.add_argument('-a', '--add', action='store_true', default=False,
        help="Query to add an entry after displaying the search results.")
    asearch.add_argument('-f', '--fetch', action='store_true', default=False,
        help="Query to fetch a PDF after displaying the search results.")
    asearch.add_argument('-o', '--open', action='store_true', default=False,
        help="Query to fetch/open a PDF after displaying the search results.")
    asearch.set_defaults(func=cli_ads_search)


    ads_add_description = f"""
{u.BOLD}Add entries from ADS by bibcode into the bibmanager database.{u.END}

Description
  This command add BibTeX entries from ADS by specifying pairs of
  ADS bibcodes and BibTeX keys.

  Executing this command without arguments (i.e., 'bibm ads-add') launches
  an interactive prompt session allowing the user to enter multiple
  bibcode, key pairs.

  By default, added entries replace previously existent entries in the
  bibmanager database.

  With the optional arguments -f/--fetch or -o/--open, the code will
  attempt to fetch and open (respectively) the associated PDF files
  of the added entries.

Examples
  # Let's search and add the greatest astronomy PhD thesis of all times:
  bibm ads-search
  author:"^payne, cecilia" doctype:phdthesis

  Title: Stellar Atmospheres; a Contribution to the Observational Study of High
         Temperature in the Reversing Layers of Stars.
  Authors: Payne, Cecilia Helena
  adsurl:  https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P
  bibcode: 1925PhDT.........1P

  # Add the entry to the bibmanager database:
  bibm ads-add 1925PhDT.........1P Payne1925phdStellarAtmospheres"""
    ads_add = sp.add_parser('ads-add', description=ads_add_description,
        usage="bibm ads-add [-h] [-f] [-o] [bibcode key]",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ads_add.add_argument('bibcode', action='store', nargs='?',
        help='The ADS bibcode of an entry.')
    ads_add.add_argument('key', action='store', nargs='?',
        help='BibTeX key to assign to the entry.')
    ads_add.add_argument('-f', '--fetch', action='store_true', default=False,
        help="Fetch the PDF of the added entries.")
    ads_add.add_argument('-o', '--open', action='store_true', default=False,
        help="Fetch and open the PDF of the added entries.")
    ads_add.set_defaults(func=cli_ads_add)


    ads_update_description = f"""
{u.BOLD}Update bibmanager database cross-checking entries with ADS.{u.END}

Description
  This command triggers an ADS search of all entries in the bibmanager
  database that have a 'bibcode' field.  Replacing these entries with
  the output from ADS.

  The main utility of this command is to auto-update entries that
  were added as arXiv version, with their published version.

  For arXiv updates, this command updates automatically the year and
  journal of the key (where possible).  This is done by searching for
  the year and the string 'arxiv' in the key, using the bibcode info.

  For example, an entry with key 'NameEtal2010arxivGJ436b' whose bibcode
  changed from '2010arXiv1007.0324B' to '2011ApJ...731...16B', will have
  a new key 'NameEtal2011apjGJ436b'.
  To disable this feature, set the 'update_keys' optional argument to no.
"""
    ads_update = sp.add_parser('ads-update', description=ads_update_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ads_update.add_argument('update', action='store', metavar='update_keys',
        default='arxiv', nargs='?', choices=['no', 'arxiv'],
        #default='arxiv', nargs='?', choices=['no', 'arxiv', 'all'],
        help='Update the keys of the entries. (choose from: {%(choices)s}, '
             'default: %(default)s).')
    ads_update.set_defaults(func=cli_ads_update)


    fetch_description = f"""
{u.BOLD}Fetch a PDF file from ADS.{u.END}

Description
  This command attempts to fetch from ADS the PDF for a Bibtex entry
  in the Bibmanager database (or any valid ADS entry).  The request is
  made to the Journal, then the ADS server, and lastly to ArXiv
  until one succeeds.  The entry is specified by either the BibTex
  key or ADS bibcode, these can be specified on the initial command,
  or will be queried after through the prompt (see examples).

  If the output PDF filename is not specified, the routine will
  guess a name with this syntax:  LastnameYYYY_Journal_vol_page.pdf
  Obviously, requests for entries not in the database can be made only
  by ADS bibcode (and auto-completion wont be able to predict their
  bibcode IDs).

  Set the -o/--open flag to open the PDF right after fetching.

Examples
  # Fetch setting the BibTex key:
  bibm fetch BurbidgeEtal1957rvmpStellarElementSynthesis
  Fetching PDF file from Journal website:
  Saved PDF to: '/home/user/.bibmanager/pdf/Burbidge1957_RvMP_29_547.pdf'.

  # Fetch by ADS bibcode:
  bibm fetch 1957RvMP...29..547B

  # Fetch by ADS bibcode and setting the output filename:
  bibm fetch 1957RvMP...29..547B  Burbidge1957_stars.pdf
  Fetching PDF file from Journal website:
  Saved PDF to: '/home/user/.bibmanager/pdf/Burbidge1957_stars.pdf'.

  # Use prompt to find the BibTex entry:
  bibm fetch
  Syntax is:  key: KEY_VALUE FILENAME
         or:  bibcode: BIBCODE_VALUE FILENAME
  (FILENAME is optional.  Press 'tab' for autocomplete)
  key: BurbidgeEtal1957rvmpStellarElementSynthesis
  Fetching PDF file from Journal website:
  Saved PDF to: '/home/user/.bibmanager/pdf/Burbidge1957_RvMP_29_547.pdf'.

"""
    fetch = sp.add_parser('fetch', description=fetch_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    fetch.add_argument('keycode', action='store', nargs='?',
        help='Either a BibTex key or an ADS bibcode identifier.')
    fetch.add_argument('filename', action='store', nargs='?',
        help='Name for fetched PDF file.')
    fetch.add_argument('-o', '--open', action='store_true', default=False,
        help="Open the fetched PDF if the request succeeded.")
    fetch.set_defaults(func=cli_fetch)


    open_description = f"""
{u.BOLD}Open the PDF file of a BibTex entry in the database.{u.END}

Description
  This command opens the PDF file associated to a Bibtex entry in
  the Bibmanager database.  The entry is specified by either its
  BibTex key, its ADS bibcode, or its PDF filename.  These can be
  specified on the initial command, or will be queried through the
  prompt (with auto-complete help).

  If the user requests a PDF for an entry without a PDF file but with
  an ADS bibcode, Bibmanager will ask if the user wants to fetch the
  PDF from ADS.

Examples
  # Open setting the BibTex key:
  bibm open BurbidgeEtal1957rvmpStellarElementSynthesis

  # Open setting the ADS bibcode:
  bibm open 1957RvMP...29..547B

  # Open setting the PDF filename:
  bibm open Burbidge1957_RvMP_29_547.pdf

  # Use prompt to find the BibTex entry:
  bibm open
  Syntax is:  key: KEY_VALUE
         or:  bibcode: BIBCODE_VALUE
         or:  pdf: PDF_VALUE
  (Press 'tab' for autocomplete)
  key: BurbidgeEtal1957rvmpStellarElementSynthesis
"""
    pdf_open = sp.add_parser('open', description=open_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    pdf_open.add_argument('keycode', action='store', nargs='?',
        help='Either a BibTex key, an ADS bibcode, or a PDF filename.')
    pdf_open.set_defaults(func=cli_open)


    link_description = f"""
{u.BOLD}Link a PDF file to a BibTex entry in the database.{u.END}

Description
  This command manually links an existing PDF file to a Bibtex entry
  in the Bibmanager database.  The PDF file is moved to the home/pdf/
  folder.  The entry is specified by either the BibTex key or ADS bibcode,
  these can be specified on the initial command, or will be queried
  after through the prompt (see examples).

  If the output PDF filename is not specified, the code will preserve
  the file name.  If the user sets 'guess' as filename, the code will
  guess a name based on the BibTex information.

Examples
  # Link a downloaded PDF file to an entry:
  bibm pdf 1957RvMP...29..547B ~/Downloads/Burbidge1957.pdf
  Saved PDF to: '/home/user/.bibmanager/pdf/Burbidge1957.pdf'.

  # Link a downloaded PDF file (guessing the name from BibTex):
  bibm pdf 1957RvMP...29..547B ~/Downloads/Burbidge1957.pdf guess
  Saved PDF to: '/home/user/.bibmanager/pdf/Burbidge1957_RvMP_29_547.pdf'.

  # Link a downloaded PDF file (renaming file):
  bibm pdf 1957RvMP...29..547B ~/Downloads/Burbidge1957.pdf BurbidgeEtal_1957.pdf
  Saved PDF to: '/home/user/.bibmanager/pdf/BurbidgeEtal_1957.pdf'.

  # Use prompt to find the BibTex entry:
  bibm pdf
  Syntax is:  key: KEY_VALUE PDF FILENAME
         or:  bibcode: BIBCODE_VALUE PDF FILENAME
  (FILENAME is optional.  Press 'tab' for autocomplete)
  key: BurbidgeEtal1957rvmpStellarElementSynthesis ~/Downloads/Burbidge1957.pdf
  Saved PDF to: '/home/user/.bibmanager/pdf/Burbidge1957.pdf'.
"""
    link = sp.add_parser('pdf', description=link_description,
        usage="bibm pdf [-h] [keycode pdf] [filename]",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    link.add_argument('keycode', action='store', nargs='?',
        help='Either a BibTex key or an ADS bibcode identifier.')
    link.add_argument('pdf', action='store', nargs='?',
        help='Path to PDF file to link to entry.')
    link.add_argument('filename', action='store', nargs='?',
        help='New name for linked PDF file.')
    link.set_defaults(func=cli_link)

    # Parse command-line args:
    args, unknown = parser.parse_known_args()

    # Version check:
    pickle_ver = bm.get_version()
    if version.parse(__version__) < version.parse(pickle_ver):
        print(f"Bibmanager version ({__version__}) is older than saved "
              f"database.  Please update to a version >= {pickle_ver}.")
        return
    elif version.parse(pickle_ver) < version.parse(__version__):
        print(f"Updating database file from version {pickle_ver} to "
              f"version {__version__}.")
        bm.init(bibfile=u.BM_BIBFILE())

    if not hasattr(args, 'func'):
        parser.print_help()
    # Make bibmanager calls:
    else:
        args.func(args)


if __name__ == "__main__":
    main()
