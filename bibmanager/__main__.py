import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import bibmanager as bm


def main():
    """
    Bibmanager command-line interface.

    Partially inspired by these:
    - https://stackoverflow.com/questions/7869345/
    - https://stackoverflow.com/questions/32017020/
    """
    # Parser Documentation:
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

    init_description="""Initialization."""
    merge_description="""Merge a bibfile into bibmanager."""
    edit_description="""Edit manually the bibmanager database."""
    add_description="""Add entries to bibmanager database."""
    search_description="""Search in bibmanager database."""
    export_description="""Export bibtex."""
    setup_description="""Set bibmanager configuration."""
    bibtex_description="""Generate bibtex."""
    latex_description="""latex compilation."""
    pdftex_description="""pdftex compilation."""
    asearch_description="""ADS search."""
    aadd_description="""ADS add."""
    aupdate_description="""ADS update."""

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        #usage='%(prog)s [command] [options] [arguments]',
        )

    parser.add_argument('-v', '--version', action='version',
        help="Show bibm's version number.",
        version='bibmanager version {:s}'.format(bm.__version__))

    def my_func(args):
        """
        Placeholder.
        """
        print(args.bibfile)

    # Database Management:
    init = argparse.ArgumentParser(add_help=False)
    init.add_argument("bibfile", action="store", nargs='?', help="A file.bib")

    merge = argparse.ArgumentParser(add_help=False)
    merge.add_argument("bibfile", action="store", help="A file.bib")
    merge.add_argument("take", action="store", nargs='?',
        help="Decision making protocol")
    merge.set_defaults(func=my_func)

    search = argparse.ArgumentParser(add_help=False)
    search.add_argument('-a', '--author', action='store',
        help='Search by author.')
    search.add_argument('-y', '--year', action='store',
        help='Restrict search to a year (e.g., -y 2018) or to a year range '
             '(e.g., -y 2018-2020).')
    search.add_argument('-t', '--title', action='store',
        help='Search by keywords in title.')

    add = argparse.ArgumentParser(add_help=False)
    add.add_argument("take", action="store", nargs='?',
        help="Decision making protocol")

    export = argparse.ArgumentParser(add_help=False)
    export.add_argument("bibfile", action="store", nargs='?',
        help="A .bib or .bbl file")

    # Latex Management:
    bibtex = argparse.ArgumentParser(add_help=False)
    bibtex.add_argument("texfile", action="store", help="A .tex file")
    bibtex.add_argument("bibfile", action="store", nargs='?',
        help="A .bib file (output)")

    latex = argparse.ArgumentParser(add_help=False)
    latex.add_argument("texfile", action="store", help="A .tex file")

    pdftex = argparse.ArgumentParser(add_help=False)
    pdftex.add_argument("texfile", action="store", help="A .tex file")

    # ADS Management:
    asearch = argparse.ArgumentParser(add_help=False)
    asearch.add_argument('querry', action='store', help='Querry input.')

    aadd = argparse.ArgumentParser(add_help=False)
    aadd.add_argument('adskeys', action='store', nargs='+',
        help='ADS keys.')


    sp = parser.add_subparsers(title="These are the bibmanager commands",
        description=main_description)
    # Database Management:
    sp.add_parser('init',   parents=[init],   description=init_description)
    sp.add_parser('merge',  parents=[merge],  description=merge_description)
    sp.add_parser('edit',   description=edit_description)
    sp.add_parser('add',    parents=[add],    description=add_description)
    sp.add_parser('search', parents=[search], description=search_description)
    sp.add_parser('export', parents=[export], description=export_description)
    sp.add_parser('setup',  description=setup_description)
    # Latex Management:
    sp.add_parser('bibtex', parents=[bibtex], description=bibtex_description)
    sp.add_parser('latex',  parents=[latex],  description=latex_description)
    sp.add_parser('pdftex', parents=[pdftex], description=pdftex_description)
    # ADS Management:
    sp.add_parser('ads-search', parents=[asearch], description=asearch_description)
    sp.add_parser('ads-add',    parents=[aadd], description=aadd_description)
    sp.add_parser('ads-update', description=aupdate_description)

    # Parse command-line args:
    args, unknown = parser.parse_known_args()
    # Make bibmanager calls:
    args.func(args)


if __name__ == "__main__":
    main()
