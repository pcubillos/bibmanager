# Copyright (c) 2018-2019 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import re
import argparse
import textwrap

import prompt_toolkit
from prompt_toolkit.history import FileHistory

from . import bib_manager    as bm
from . import latex_manager  as lm
from . import config_manager as cm
from . import ads_manager    as am
from . import utils as u
from .__init__ import __version__ as ver


# Parser Main Documentation:
main_description = """
BibTeX Database Management:
---------------------------
  reset       Reset the bibmanager database.
  merge       Merge a BibTeX file into the bibmanager database.
  edit        Edit the bibmanager database in a text editor.
  add         Add entries into the bibmanager database.
  search      Search entries in the bibmanager database.
  export      Export the bibmanager database into a bib file.
  cleanup     Clean up a bibtex file of duplicates and outdated entries.
  config      Manage the bibmanager configuration parameters.

LaTeX Management:
----------------
  bibtex      Generate a BibTeX file from a LaTeX file.
  latex       Compile a LaTeX file with the latex command.
  pdflatex    Compile a LaTeX file with the pdflatex command.

ADS Management:
---------------
  ads-search  Do a querry on ADS.
  ads-add     Add entries from ADS by bibcode into the bibmanager database.
  ads-update  Update bibmanager database cross-checking entries with ADS.

For additional details on a specific command, see 'bibm command -h'.
See the full bibmanager docs at https://bibmanager.readthedocs.io

Copyright (c) 2018-2019 Patricio Cubillos and contributors.
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
    session = prompt_toolkit.PromptSession(
        history=FileHistory(u.BM_HISTORY_SEARCH))
    inputs = session.prompt("(Press 'tab' for autocomplete)\n",
        auto_suggest=u.AutoSuggestCompleter(),
        completer=u.search_completer,
        complete_while_typing=False)
    # Parse inputs:
    authors  = re.findall(r'author:"([^"]+)', inputs)
    title_kw = re.findall(r'title:"([^"]+)',  inputs)
    years    = re.search(r'year:[\s]*([^\s]+)',    inputs)
    key      = re.findall(r'key:[\s]*([^\s]+)',     inputs)
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
        bm.display_bibs(labels=None, bibs=matches)
        return

    for match in matches:
        title = textwrap.fill(f"Title: {match.title}, {match.year}",
                              width=78, subsequent_indent='       ')
        authors = textwrap.fill("Authors: "
                                f"{match.get_authors(short=args.verb<2)}",
                                width=78, subsequent_indent='         ')
        keys = f"\nkey: {match.key}"
        if args.verb > 0 and match.eprint is not None:
            keys = f"\narXiv url: http://arxiv.org/abs/{match.eprint}{keys}"
        if args.verb > 0 and match.adsurl is not None:
            keys = f"\nADS url:   {match.adsurl}{keys}"
            keys = f"\nbibcode:   {match.bibcode}{keys}"
        print(f"\n{title}\n{authors}{keys}")


def cli_export(args):
    """Command-line interface for export call."""
    path, bibfile = os.path.split(os.path.realpath(args.bibfile))
    if not os.path.exists(path):
        print(f"\nError: Output dir does not exists: '{path}'")
        return
    bibfile, extension = os.path.splitext(bibfile)
    if extension == ".bib":
        bm.export(bm.load(), bibfile=args.bibfile)
    elif extension == ".bbl":
        print("\nSorry, export to .bbl output is not implemented yet.")
        return
    else:
        print(f"\nError: Invalid file extension ('{extension}'), must be "
               "'.bib' or '.bbl'.")


def cli_cleanup(args):
    """Clean up"""
    bibs = bm.loadfile(args.bibfile)
    if args.ads:
        updated = am.update(base=bibs)
        if updated is not None:
            bibs = updated
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
    lm.compile_latex(args.texfile, args.paper)


def cli_pdflatex(args):
    """Command-line interface for pdflatex call."""
    lm.compile_pdflatex(args.texfile)


def cli_ads_search(args):
    """Command-line interface for ads-search call."""
    if args.next:
        querry = None
    else:
        session = prompt_toolkit.PromptSession(
            history=FileHistory(u.BM_HISTORY_ADS))
        querry = session.prompt("(Press 'tab' for autocomplete)\n",
            auto_suggest=u.AutoSuggestCompleter(),
            completer=u.ads_completer,
            complete_while_typing=False).strip()
        if querry == "" and os.path.exists(u.BM_CACHE):
            querry = None
        elif querry == "":
            return
    am.manager(querry)


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
    am.add_bibtex(bibcodes, keys)


def cli_ads_update(args):
    """Command-line interface for ads-update call."""
    update_keys = args.update == 'arxiv'
    am.update(update_keys=update_keys)


def main():
    """
    Bibmanager command-line interface.

    Partially inspired by these:
    - https://stackoverflow.com/questions/7869345/
    - https://stackoverflow.com/questions/32017020/
    """
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-v', '--version', action='version',
        help="Show bibmanager's version.",
        version=f'bibmanager version {ver}')

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

  Multiple author, title keyword, and year querries act with AND logic;
  whereas multiple-key querries and multiple-bibcode querries act with OR
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

  # Seach by author, year, and title words/phrases (using AND logic):
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
  There are five parameters that can be set by the user:
  - style       sets the color-syntax style of displayed BibTeX entries.
  - text_editor sets the text editor for 'bibm edit' calls.
  - paper       sets the default paper format for latex compilation.
  - ads_token   sets the token required for ADS requests.
  - ads_display sets the number of entries to show at once for ADS searches.

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
{u.BOLD}Do a querry on ADS.{u.END}

Description
  This command enables ADS querries.  The querry syntax is identical to
  a querry in the new ADS's one-box search engine:
  https://ui.adsabs.harvard.edu.
  Here there is a detailed documentations for ADS searches:
  https://adsabs.github.io/help/search/search-syntax
  See below for typical querry examples.

  A querry will display at most 'ads_display' entries on screen at once
  (see 'bibm config ads_display').  If a querry matched more entries,
  the user can execute 'bibm ads-search -n' to display the next set of
  entries.

  Note that per ADS syntax, fields in quotes must use double quotes.

Examples
  # Search entries for author (press tab to prompt the autocompleter):
  bibm ads-search
  (Press 'tab' for autocomplete)
  author:"^Fortney, J"

  # Display the next set of entries that matched this querry:
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

  # Seach by author AND year:
  bibm ads-search
  author:"Fortney, J" year:2010
  # Seach by author AND year range:
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
        help="Display next set of entries that matched the previous querry.")
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
        usage="bibm ads-add [-h] [bibcode key]",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ads_add.add_argument('bibcode', action='store', nargs='?',
        help='The ADS bibcode of an entry.')
    ads_add.add_argument('key', action='store', nargs='?',
        help='BibTeX key to assign to the entry.')
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

    # Parse command-line args:
    args, unknown = parser.parse_known_args()

    if not hasattr(args, 'func'):
        parser.print_help()
    # Make bibmanager calls:
    else:
        args.func(args)


if __name__ == "__main__":
    main()
