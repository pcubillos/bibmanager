# Copyright (c) 2018 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

import sys
import os
import argparse
import textwrap

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import bibmanager as bm
# FINDME: Temporary hack until setting BM as a package:
import latex_manager  as lm
import config_manager as cm
from utils import BOLD, END


def cli_init(args):
    """Command-line interface for init call."""
    if args.bibfile is not None and not os.path.exists(args.bibfile):
        raise FileNotFoundError("Input bibfile '{:s}' does not exist.".
                        format(args.bibfile))
    if args.bibfile is not None:
        bibzero = " with bibfile: '{:s}'.".format(args.bibfile)
        args.bibfile = os.path.realpath(args.bibfile)
    else:
        bibzero = "."
    print("Initializing new bibmanager database{:s}".format(bibzero))
    bm.init(args.bibfile)


def cli_merge(args):
    """Command-line interface for merge call."""
    if args.bibfile is not None and not os.path.exists(args.bibfile):
        raise FileNotFoundError("Input bibfile '{:s}' does not exist.".
                        format(args.bibfile))
    if args.bibfile is not None:
        args.bibfile = os.path.realpath(args.bibfile)
    bm.merge(bibfile=args.bibfile, take=args.take)
    print("\nMerged new bibfile '{:s}' into bibmanager database.".
          format(args.bibfile))


def cli_edit(args):
    """Command-line interface for edit call."""
    bm.edit()


def cli_add(args):
    """Command-line interface for add call."""
    bm.add_entries(take=args.take)


def cli_search(args):
    """Command-line interface for init call."""
    year = args.year
    # Cast year string to integer or list of integers:
    if year is None:
        year = None
    elif len(year) == 4 and year.isnumeric():
        year = int(year)
    elif len(year) == 5 and year.startswith('-') and year[1:].isnumeric():
        year = [0, int(year[1:])]
    elif len(year) == 5 and year.endswith('-') and year[0:4].isnumeric():
        year = [int(year[0:4]), 9999]
    elif len(year) == 9 and year[0:4].isnumeric() and year[5:].isnumeric():
        year = [int(year[0:4]), int(year[5:9])]
    else:
        raise ValueError("Invalid input year format: {:s}".format(year))

    matches = bm.search(args.author, year, args.title)

    # Display outputs depending on the verb level:
    if args.verb >= 3:
        bm.display_bibs(labels=None, bibs=matches)
        return

    wrap_kw = {'width':80, 'subsequent_indent':"   "}
    for match in matches:
        title = textwrap.fill("Title: {:s}, {:d}".format(match.title,
            match.year), **wrap_kw)
        authors = textwrap.fill("Authors: {:s}".format(
            match.get_authors(short=args.verb<2)), **wrap_kw)
        keys = "\nbibkey: {:s}".format(match.key)
        if args.verb > 0 and match.eprint is not None:
            keys = "\narXiv url: http://arxiv.org/abs/{:s}{:s}".format(
                match.eprint, keys)
        if args.verb > 0 and match.adsurl is not None:
            keys = "\nADS url:   {:s}{:s}".format(match.adsurl, keys)
        print("\n{:s}\n{:s}{:s}".format(title, authors, keys))


def cli_export(args):
    """Command-line interface for export call."""
    path, bfile = os.path.split(os.path.realpath(args.bibfile))
    if not os.path.exists(path):
        raise FileNotFoundError("Output dir does not exists: '{:s}'".
                                format(path))
    # TBD: Check for file extension
    bm.export(bm.load(), bibfile=args.bibfile)

def cli_config(args):
    """Command-line interface for config call."""
    if args.key is None:
        cm.display()
    elif args.value is None:
        cm.help(args.key)
    else:
        cm.set(args.key, args.value)

def cli_bibtex(args):
    """Command-line interface for add call."""
    lm.build_bib(args.texfile, args.bibfile)


def cli_latex(args):
    """Command-line interface for latex call."""
    lm.compile_latex(args.texfile, args.paper)


def cli_pdflatex(args):
    """Command-line interface for pdflatex call."""
    lm.compile_pdflatex(args.texfile)


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
        version='bibmanager version {:s}'.format(bm.__version__))

    # Parser Main Documentation:
    main_description = """
{:s}BibTeX Database Management:{:s}
  init        Initialize bibmanager database (from scratch).
  merge       Merge a bibfile into the bibmanager database.
  edit        Edit the bibmanager database in a text editor.
  add         Add entries into the bibmanager database.
  search      Search in database by author, year, and/or title.
  export      Export the bibmanager database into a bibfile.
  config      Set bibmanager configuration parameters.

{:s}LaTeX Management:{:s}
  bibtex      Generate a bibtex file from a tex file.
  latex       Compile a latex file with the latex directive.
  pdflatex    Compile a latex file with the pdflatex directive.

{:s}ADS Management:{:s}
  ads-search  Search in ADS.
  ads-add     Add entry from ADS into the bibmanager database.
  ads-update  Update bibmanager database cross-checking with ADS database.

For additional details on a specific command, see 'bibm command --help'.
See the full bibmanager docs at http://pcubillos.github.io/bibmanager

Copyright (c) 2018 Patricio Cubillos and contributors.
bibmanager is open-source software under the MIT license, see:
https://github.com/pcubillos/bibmanager/blob/master/LICENSE
""".format(BOLD, END, BOLD, END, BOLD, END)

    # And now the sub-commands:
    sp = parser.add_subparsers(title="These are the bibmanager commands",
        description=main_description, metavar='command')

    # Database Management:
    init_description = """
{:s}Initialize the bibmanager database.{:s}

Description
  This command initializes the bibmanager database (from scratch).
  It creates a .bibmanager/ folder in the user folder (if it does not
  exists already), and it (re)sets the bibmanager configuration to
  its default values.

  If the user provides the 'bibfile' argument, this command will
  populate the database with the entries from that file; otherwise,
  it will set an empty database.

  Note that this will overwrite any pre-existing database.  In
  principle the user should not execute this command more than once
  in a given CPU.""".format(BOLD, END)
    init = sp.add_parser('init', description=init_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    init.add_argument("bibfile", action="store", nargs='?',
        help="Path to an existing bibfile.")
    init.set_defaults(func=cli_init)

    merge_description = """
{:s}Merge a bibfile into the bibmanager database.{:s}

Description
  This commands merges the content from an input bibfile with the
  bibmanager database.

  The optional 'take' arguments defines the protocol for possible-
  duplicate entries.  Either take the 'old' entry (database), take
  the 'new' entry (bibfile), or 'ask' the user through the prompt
  (displaying the alternatives).  bibmanager considers four fields
  to check for duplicates: doi, isbn, adsurl, and eprint.

  Additionally, bibmanager considers two more cases (always asking):
  (1) new entry has duplicate key but different content, and
  (2) new entry has duplicate title but different key.
""".format(BOLD, END)
    merge = sp.add_parser('merge', description=merge_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    merge.add_argument("bibfile", action="store",
        help="Path to an existing bibfile.")
    merge.add_argument("take", action="store", nargs='?', metavar='take',
        help="Decision protocol for duplicates (choose: {%(choices)s}, "
        "default: %(default)s)", choices=['old','new','ask'], default='old')
    merge.set_defaults(func=cli_merge)

    edit_description = """
{:s}Edit the bibmanager database.{:s}

Description
  This command let's you manually edit the bibmanager database,
  in your pre-defined text editor.  Once finished editing, save and
  close the text editor, and press ENTER in the terminal to
  incorporate the edits (edits after continuing on the terminal won't
  count).

  bibmanager selects the OS default text editor.  But the user can
  set a preferred editor, see 'bibm config -h' for more information.
""".format(BOLD, END)
    edit = sp.add_parser('edit', description=edit_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    edit.set_defaults(func=cli_edit)

    search_description = """
{:s}Search entries in the bibmanager database.{:s}

Description
  This command allows the user to search for entries in the bibmanager
  database by authors, years, and keywords in title.  The matching
  results are displayed on screen according to the specified verbosity.
  For search arguments that include a blank space, the user can set
  the string within quotes.

  The user can restrict the search to one or more authors, and can
  request a first-author match by including the '^' character before
  an author name (see examples below).

  The user can restrict the publication year to an specific year,
  to a range of years, or to open-end range of years (see examples
  below).

  Finally, the user can restrict the search to multiple strings in
  the title (see examples below).  Note these are case-insensitive.

  There are four levels of verbosity (see examples below):
  - zero shows the title, year, first author, and bibkey;
  - one adds the ADS and arXiv urls;
  - two adds the full list of authors;
  - and three displays the full BibTeX entry.

Examples
  # Search by last name:
  bibm search -a LastName
  # Search by last name and initials (note blanks require one to use quotes):
  bibm search -a 'LastName, F'
  # Search by first-author only:
  bibm search -a '^LastName, F'
  # Search multiple authors:
  bibm search -a 'LastName' 'NachName'

  # Search on specific year:
  bibm search -a 'Author, I' -y 2017
  # Search anything past the specified year:
  bibm search -a 'Author, I' -y 2017-
  # Search anything up to the specified year:
  bibm search -a 'Author, I' -y -2017
  # Search anything between the specified years:
  bibm search -a 'Author, I' -y 2012-2017

  # Seach by author and with keywords on title:
  bibm search -a 'Author, I' -t 'HD 209458' 'HD 189733'

  # Display title, year, first author, and bibkey:
  bibm search -a 'Author, I'
  # Display title, year, first author, and all keys/urls:
  bibm search -a 'Author, I' -v
  # Display title, year, author list, and all keys/urls:
  bibm search -a 'Author, I' -vv
  # Display full BibTeX entry:
  bibm search -a 'Author, I' -vvv
""".format(BOLD, END)
    search = sp.add_parser('search', description=search_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    search.add_argument('-a', '--author', action='store', nargs='*',
        help='Search by author.')
    search.add_argument('-y', '--year', action='store',
        help='Restrict search to a year (e.g., -y 2018) or to a year range '
             '(e.g., -y 2018-2020).')
    search.add_argument('-t', '--title', action='store', nargs='*',
        help='Search by keywords in title.')
    search.add_argument('-v', '--verb', action='count', default=0,
        help='Set output verbosity.')
    search.set_defaults(func=cli_search)

    add_description = """
{:s}Add entries to the bibmanager database.{:s}

Description
  This command allows the user to manually add BibTeX entries into
  the bibmanager database through the terminal prompt.

  The optional 'take' arguments defines the protocol for possible-
  duplicate entries.  Either take the 'old' entry (database), take
  the 'new' entry (bibfile), or 'ask' the user through the prompt
  (displaying the alternatives).  bibmanager considers four fields
  to check for duplicates: doi, isbn, adsurl, and eprint.

  Additionally, bibmanager considers two more cases (always asking):
  (1) new entry has duplicate key but different content, and
  (2) new entry has duplicate title but different key.
""".format(BOLD, END)
    add = sp.add_parser('add', description=add_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add.add_argument("take", action="store", nargs='?', metavar='take',
        help="Decision protocol for duplicates (choose: {%(choices)s}, "
        "default: %(default)s)", choices=['old','new','ask'], default='old')
    add.set_defaults(func=cli_add)

    export_description = """
{:s}Export bibmanager database to bib file.{:s}

Description
  Export the entire bibmanager database into a bibliography file in
  .bib or .bbl format according to the file extension of the
  'bibfile' argument (TBD: for the moment, only export to .bib).
""".format(BOLD, END)
    export = sp.add_parser('export', description=export_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    export.add_argument("bibfile", action="store",
        help="Path to an output bibfile.")
    export.set_defaults(func=cli_export)

    config_description = """
{:s}Manage bibmanager configuration parameters.{:s}

Description
  This command displays or sets the value of bibmanager config parameters.
  There are four parameters/keys that can be set by the user:
  - style       sets the color-syntax style of displayed BibTeX entries.
  - text_editor sets the text editor for 'bibm edit' calls.
  - paper       sets the default paper format for latex compilation.
  - ads_token   sets the token required for ADS requests.
  - ads_display sets the number of entries to show at once for ADS searches.

  The number of arguments determines the action of this command (see
  examples below):
  - with no arguments, display all available parameters and values.
  - with the 'key' argument, display detailed info on the specified
    parameter and its current value.
  - with both 'key' and 'value' arguments, set the value of the parameter.

Examples
  # Display all config parameters and values:
  bibm config
  # Display value and help for the style parameter:
  bibm config style
  # Set the value of the BibTeX color-syntax:
  bibm config style autumn
""".format(BOLD, END)
    config = sp.add_parser('config',  description=config_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    config.add_argument("key", action="store", nargs='?',
        help="A bibmanager config parameter.")
    config.add_argument("value", action="store", nargs='?',
        help="Value for a bibmanager config key.")
    config.set_defaults(func=cli_config)

    # Latex Management:
    bibtex_description = """
{:s}Generate a bibfile from given texfile.{:s}

Description
  This commands generates a bibfile by searching for the citation
  keys in the input .tex file, and stores the output .bib file in
  the file name determined by the \\bibliography{{...}} call in the
  .tex file.  Alternatively, the user can specify the name of the
  output .bib file with the bibfile argument.

  Any citation key not found in the bibmanager database, will be
  shown on the screen prompt.
""".format(BOLD, END)
    bibtex = sp.add_parser('bibtex', description=bibtex_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    bibtex.add_argument("texfile", action="store",
        help="Path to an existing texfile.")
    bibtex.add_argument("bibfile", action="store", nargs='?',
        help="Path to an output bibfile.")
    bibtex.set_defaults(func=cli_bibtex)

    latex_description="""
{:s}Compile a .tex file using the latex command.{:s}

Description
  This command compiles a latex file using the latex command,
  executing the following calls:
  - Compute a bibfile out of the citation calls in the .tex file.
  - Remove all outputs from previous compilations.
  - Call latex, bibtex, latex, latex to produce a .dvi file.
  - Call dvi2ps and ps2pdf to produce the final .pdf file.

  Prefer this command over the pdflatex command when the .tex file
  contains .ps or .eps figures (as opposed to .pdf, .png, or .jpeg).

  Note that the user does not necessarily need to be in the dir
  where the latex files are.
""".format(BOLD, END)
    latex = sp.add_parser('latex', description=latex_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    latex.add_argument("texfile", action="store",
        help="Path to an existing texfile.")
    latex.add_argument("paper", action="store", nargs='?',
        help="Paper format, e.g., letter or A4 (default=%(default)s).",
        default=cm.get('paper'))
    latex.set_defaults(func=cli_latex)

    pdflatex_description = """
{:s}Compile a .tex file using the pdflatex command.{:s}

Description
  This command compiles a latex file using the pdflatex command,
  executing the following calls:
  - Compute a bibfile out of the citation calls in the .tex file.
  - Remove all outputs from previous compilations.
  - Call pdflatex, bibtex, pdflatex, pdflatex to produce a .pdf file.

  Prefer this command over the latex command when the .tex file
  contains .pdf, .png, or .jpeg figures (as opposed to .ps or .eps).

  Note that the user does not necessarily need to be in the dir
  where the latex files are.
""".format(BOLD, END)
    pdflatex = sp.add_parser('pdflatex', description=pdflatex_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    pdflatex.add_argument("texfile", action="store",
        help="Path to an existing texfile.")
    pdflatex.set_defaults(func=cli_pdflatex)

    # ADS Management:
    asearch_description = """ADS search."""
    asearch = sp.add_parser('ads-search', description=asearch_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    asearch.add_argument('querry', action='store', help='Querry input.')

    aadd_description = """ADS add."""
    aadd = sp.add_parser('ads-add', description=aadd_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    aadd.add_argument('adskeys', action='store', nargs='+',
        help='ADS keys.')

    aupdate_description = """ADS update."""
    aupdate = sp.add_parser('ads-update', description=aupdate_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)


    # Parse command-line args:
    args, unknown = parser.parse_known_args()
    # Make bibmanager calls:
    args.func(args)


if __name__ == "__main__":
    main()
