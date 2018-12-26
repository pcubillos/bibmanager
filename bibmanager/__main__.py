# Copyright (c) 2018 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import bibmanager as bm


def cli_init(args):
    """
    Command-line interface for init call.
    """
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
    """
    Command-line interface for merge call.
    """
    if args.bibfile is not None and not os.path.exists(args.bibfile):
        raise FileNotFoundError("Input bibfile '{:s}' does not exist.".
                        format(args.bibfile))
    if args.bibfile is not None:
        args.bibfile = os.path.realpath(args.bibfile)
    bm.merge(bibfile=args.bibfile, take=args.take)
    print("\nMerged new bibfile '{:s}' into bibmanager database.".
          format(args.bibfile))


def cli_edit(args):
    """
    Command-line interface for edit call.
    """
    bm.edit()


def cli_add(args):
    """
    Command-line interface for add call.
    """
    pass


def cli_search(args):
    """
    Command-line interface for init call.
    """
    pass


def cli_export(args):
    """
    Command-line interface for export call.
    """
    pass

def main():
    """
    Bibmanager command-line interface.

    Partially inspired by these:
    - https://stackoverflow.com/questions/7869345/
    - https://stackoverflow.com/questions/32017020/
    """

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        #usage='%(prog)s [command] [options] [arguments]',
        )

    parser.add_argument('-v', '--version', action='version',
        help="Show bibm's version number.",
        version='bibmanager version {:s}'.format(bm.__version__))

    # Parser Main Documentation:
    main_description = """
BibTeX Database Management:
  init        Initialize bibmanager database (from scratch).
  merge       Merge a bibfile into the bibmanager database.
  edit        Edit the bibmanager database in a text editor.
  add         Add entries into the bibmanager database.
  search      Search in database by author, year, and/or title.
  export      Export the bibmanager database into a bibfile.
  setup       Set bibmanager configuration parameters.

LaTeX Management:
  bibtex      Generate a bibtex file from a tex file.
  latex       Compile a latex file with the latex directive.
  pdftex      Compile a latex file with the pdflatex directive.

ADS Management:
  ads-search  Search in ADS.
  ads-add     Add entry from ADS into the bibmanager database.
  ads-update  Update bibmanager database cross-checking with ADS database.

For additional details on a specific command, see 'bibm command --help'.
See the full bibmanager docs at http://pcubillos.github.io/bibmanager"""

    # And now the sub-commands:
    sp = parser.add_subparsers(title="These are the bibmanager commands",
        description=main_description, metavar='command')

    # Database Management:
    init_description = """
Initialize the bibmanager database.

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
  in a given CPU."""
    init = sp.add_parser('init', description=init_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    init.add_argument("bibfile", action="store", nargs='?',
        help="Path to an existing bibfile.")
    init.set_defaults(func=cli_init)

    merge_description = """
Merge a bibfile into the bibmanager database.

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
  (2) new entry has duplicate title but different key."""
    merge = sp.add_parser('merge', description=merge_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    merge.add_argument("bibfile", action="store",
        help="Path to an existing bibfile.")
    merge.add_argument("take", action="store", nargs='?', metavar='take',
        help="Decision protocol for duplicates (choose: {%(choices)s}, "
        "default: %(default)s)", choices=['old','new','ask'], default='old')
    merge.set_defaults(func=cli_merge)

    edit_description = """
Edit the bibmanager database.

Description
  This command let's you manually edit the bibmanager database,
  in your pre-defined text editor.  Once finished editing, save and
  close the text editor, and press ENTER in the terminal to
  incorporate the edits (edits after continuing on the terminal won't
  count).

  bibmanager selects the OS default text editor.  But the user can
  set a preferred editor, see 'bibm setup -h' for more information."""
    edit = sp.add_parser('edit', description=edit_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    edit.set_defaults(func=cli_edit)

    search_description = """Search in bibmanager database."""
    search = sp.add_parser('search', description=search_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    search.add_argument('-a', '--author', action='store',
        help='Search by author.')
    search.add_argument('-y', '--year', action='store',
        help='Restrict search to a year (e.g., -y 2018) or to a year range '
             '(e.g., -y 2018-2020).')
    search.add_argument('-t', '--title', action='store',
        help='Search by keywords in title.')

    add_description = """Add entries to bibmanager database."""
    add = sp.add_parser('add', description=add_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add.add_argument("take", action="store", nargs='?',
        help="Decision making protocol")

    export_description = """Export bibtex."""
    export = sp.add_parser('export', description=export_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    export.add_argument("bibfile", action="store", nargs='?',
        help="A .bib or .bbl file")

    setup_description="""Set bibmanager configuration."""
    setup = sp.add_parser('setup',  description=setup_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # Latex Management:
    bibtex_description="""Generate bibtex."""
    bibtex = sp.add_parser('bibtex', description=bibtex_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    bibtex.add_argument("texfile", action="store", help="A .tex file")
    bibtex.add_argument("bibfile", action="store", nargs='?',
        help="A .bib file (output)")

    latex_description="""latex compilation."""
    latex = sp.add_parser('latex', description=latex_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    latex.add_argument("texfile", action="store", help="A .tex file")

    pdftex_description="""pdftex compilation."""
    pdftex = sp.add_parser('pdftex', description=pdftex_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    pdftex.add_argument("texfile", action="store", help="A .tex file")

    # ADS Management:
    asearch_description="""ADS search."""
    asearch = sp.add_parser('ads-search', description=asearch_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    asearch.add_argument('querry', action='store', help='Querry input.')

    aadd_description="""ADS add."""
    aadd = sp.add_parser('ads-add', description=aadd_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    aadd.add_argument('adskeys', action='store', nargs='+',
        help='ADS keys.')

    aupdate_description="""ADS update."""
    aupdate = sp.add_parser('ads-update', description=aupdate_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)


    # Parse command-line args:
    args, unknown = parser.parse_known_args()
    # Make bibmanager calls:
    args.func(args)


if __name__ == "__main__":
    main()
