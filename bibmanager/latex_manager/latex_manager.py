# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

__all__ = [
    'no_comments',
    'citations',
    'parse_subtex_files',
    'build_bib',
    'clear_latex',
    'compile_latex',
    'compile_pdflatex',
]

import os
import re
import subprocess
import numpy as np

from .. import bib_manager    as bm
from .. import config_manager as cm
from .. import utils as u


def no_comments(text):
    r"""
    Remove comments from tex file, partially inspired by this:
    https://stackoverflow.com/questions/2319019

    Parameters
    ----------
    text: String
        Content from a latex file.

    Returns
    -------
    no_comments_text: String
        Input text with removed comments (as defined by latex format).

    Examples
    --------
    >>> import bibmanager.latex_manager as lm
    >>> text = r'''
    Hello, this is dog.
    % This is a comment line.
    This line ends with a comment. % A comment
    However, this is a percentage \%, not a comment.
    OK, bye.'''
    >>> print(lm.no_comments(text))
    Hello, this is dog.
    This line ends with a comment.
    However, this is a percentage \%, not a comment.
    OK, bye.
    """
    return re.sub(r"\A%.*|[^\\]%.*", "", text)


def citations(text):
    r"""
    Generator to find citations in a tex text.  Partially inspired
    by this: https://stackoverflow.com/questions/29976397

    Notes
    -----
    Act recursively in case there are references inside the square
    brackets of the cite call.  Only failing case I can think so far
    is if there are nested square brackets.

    Parameters
    ----------
    text: String
        String where to search for the latex citations.

    Yields
    ------
    citation: String
        The citation key.

    Examples
    --------
    >>> import bibmanager.latex_manager as lm
    >>> import os
    >>> # Syntax matches any of these calls:
    >>> tex = r'''
    \citep{AuthorA}.
    \citep[pre]{AuthorB}.
    \citep[pre][post]{AuthorC}.
    \citep [pre] [post] {AuthorD}.
    \citep[{\pre},][post]{AuthorE, AuthorF}.
    \citep[pre][post]{AuthorG} and \citep[pre][post]{AuthorH}.
    \citep{
     AuthorI}.
    \citep
    [][]{AuthorJ}.
    \citep[pre
     ][post] {AuthorK, AuthorL}
    \citep[see also \citealp{AuthorM}][]{AuthorN}'''
    >>> for citation in lm.citations(tex):
    >>>     print(citation, end=" ")
    AuthorA AuthorB AuthorC AuthorD AuthorE AuthorF AuthorG AuthorH AuthorI AuthorJ AuthorK AuthorL AuthorM AuthorN

    >>> # Match all of these cite calls:
    >>> tex = r'''
    \cite{AuthorA}, \nocite{AuthorB}, \defcitealias{AuthorC}.
    \citet{AuthorD}, \citet*{AuthorE}, \Citet{AuthorF}, \Citet*{AuthorG}.
    \citep{AuthorH}, \citep*{AuthorI}, \Citep{AuthorJ}, \Citep*{AuthorK}.
    \citealt{AuthorL},     \citealt*{AuthorM},
    \Citealt{AuthorN},     \Citealt*{AuthorO}.
    \citealp{AuthorP},     \citealp*{AuthorQ},
    \Citealp{AuthorR},     \Citealp*{AuthorS}.
    \citeauthor{AuthorT},  \citeauthor*{AuthorU}.
    \Citeauthor{AuthorV},  \Citeauthor*{AuthorW}.
    \citeyear{AuthorX},    \citeyear*{AuthorY}.
    \citeyearpar{AuthorZ}, \citeyearpar*{AuthorAA}.'''
    >>> for citation in lm.citations(tex):
    >>>     print(citation, end=" ")
    AuthorA AuthorB AuthorC AuthorD AuthorE AuthorF AuthorG AuthorH AuthorI AuthorJ AuthorK AuthorL AuthorM AuthorN AuthorO AuthorP AuthorQ AuthorR AuthorS AuthorT AuthorU AuthorV AuthorW AuthorX AuthorY AuthorZ AuthorAA

    >>> texfile = os.path.expanduser('~')+"/.bibmanager/examples/sample.tex"
    >>> with open(texfile) as f:
    >>>     tex = f.read()
    >>> tex = lm.no_comments(tex)
    >>> cites = [citation for citation in lm.citations(tex)]
    >>> for key in np.unique(cites):
    >>>     print(key)
    AASteamHendrickson2018aastex62
    Astropycollab2013aaAstropy
    Hunter2007ieeeMatplotlib
    JonesEtal2001scipy
    MeurerEtal2017pjcsSYMPY
    PerezGranger2007cseIPython
    vanderWaltEtal2011numpy
    """
    # This RE pattern matches:
    # - Latex commands: \defcitealias, \nocite, \cite
    # - Natbib commands: \cite + p, t, alp, alt, author, year, yearpar
    #                    (as well as their capitalized and starred versions).
    # - Zero or one square brackets (with everything in between).
    # - Zero or one square brackets (with everything in between).
    # - The content of the curly braces.
    # With zero or more blanks in between each expression.
    p = re.compile(
        r"\\(?:defcitealias|nocite|cite|"
        r"(?:[Cc]ite(?:p|alp|t|alt|author|year|yearpar)\*?))"
        r"[\s]*(\[[^\]]*\])?"
        r"[\s]*(\[[^\]]*\])?"
        r"[\s]*{([^}]+)")
    # Parse matches, do recursive call on the brakets content, yield keys:
    for left, right, cites in p.findall(text):
        # Remove blanks, strip outer commas:
        cites = "".join(cites.split()).strip(",")

        for cite in citations(left):
            yield cite
        for cite in cites.split(","):
            yield cite
        for cite in citations(right):
            yield cite


def parse_subtex_files(tex):
    """
    Recursively search for subfiles included in tex. Append their
    content at the end of tex and return.

    Parameters
    ----------
    tex: String
        String to parse.

    Returns
    -------
    tex: String
        String with appended content from any subfile.
    """
    # Remove blanks, strip outer commas:
    tex = no_comments(tex)
    # This RE pattern matches:
    # - The command: \input or \include or \subfile
    # - The content of the curly braces.
    # With zero or more blanks in between each expression.
    p = re.compile(r"\\(?:input|include|subfile)[\s]*{([^}]+)")
    # Parse matches, do recursive call on the brackets content, yield keys:
    for input_file in p.findall(tex):
        path, input_file = os.path.split(os.path.realpath(input_file))
        input_file, extension = os.path.splitext(input_file.strip())
        with open(f"{path}/{input_file}.tex", "r") as f:
            input_tex = parse_subtex_files(f.read())
        tex += input_tex
    return tex


def build_bib(texfile, bibfile=None):
    """
    Generate a .bib file from a given tex file.

    Parameters
    ----------
    texfile: String
        Name of an input tex file.
    bibfile: String
        Name of an output bib file.  If None, get bibfile name from
        bibliography call inside the tex file.

    Returns
    -------
    missing: List of strings
        List of the bibkeys not found in the bibmanager database.
    """
    # Extract path:
    path, texfile = os.path.split(os.path.realpath(texfile))
    # Remove extension:
    texfile, extension = os.path.splitext(texfile)

    if extension != ".tex":
        raise ValueError("Input file does not have a .tex extension.")

    with open(f"{path}/{texfile}.tex", "r") as f:
        tex = f.read()

    # Start at the beginning:
    beginning = tex.find(r'\begin{document}')
    if beginning > 0:
        tex = tex[beginning:]

    # Implemented into a separate function to get recursion rolling:
    tex = parse_subtex_files(tex)

    # Extract bibfile name from texfile:
    if bibfile is None:
        biblio = re.findall(r"\\bibliography{([^}]+)", tex)
        if len(biblio) == 0:
            raise Exception("No 'bibiliography' call found in tex file.")
        bibfile = f"{path}/{biblio[0].strip()}.bib"

    # Extract citation keys from texfile:
    cites = [citation for citation in citations(tex)]
    tex_keys = np.unique(cites)

    # Collect BibTeX references from keys in database:
    bibs = bm.load()
    db_keys = [bib.key for bib in bibs]

    found = np.in1d(tex_keys, db_keys, assume_unique=True)
    missing = tex_keys[np.where(np.invert(found))]
    if not np.all(found):
        print("References not found:\n{:s}".format('\n'.join(missing)))

    bibs = [bibs[db_keys.index(key)] for key in tex_keys[found]]
    bm.export(bibs, bibfile=bibfile)

    return missing


def clear_latex(texfile):
    """
    Remove by-products of previous latex compilations.

    Parameters
    ----------
    texfile: String
        Path to an existing .tex file.

    Notes
    -----
    For an input argument texfile='filename.tex', this function deletes
    the files that begin with 'filename' followed by:
      .bbl, .blg, .out, .dvi,
      .log, .aux, .lof, .lot,
      .toc, .ps,  .pdf, Notes.bib
    """
    clears = [
        '.bbl', '.blg', '.out', '.dvi',
        '.log', '.aux', '.lof', '.lot',
        '.toc', '.ps',  '.pdf', 'Notes.bib']

    # Remove extension:
    texfile = os.path.splitext(texfile)[0]

    # Delete without complaining:
    for clear in clears:
        with u.ignored(OSError):
            os.remove(f'{texfile}{clear}')


def compile_latex(texfile, paper=None):
    """
    Compile a .tex file into a .pdf file using latex calls.

    Parameters
    ----------
    texfile: String
        Path to an existing .tex file.
    paper: String
        Paper size for output.  For example, ApJ articles use letter
        format, whereas A&A articles use A4 format.

    Notes
    -----
    This function executes the following calls:
    - compute a bibfile out of the citation calls in the .tex file.
    - removes all outputs from previous compilations (see clear_latex())
    - calls latex, bibtex, latex, latex to produce a .dvi file
    - calls dvips to produce a .ps file, redirecting the output to
      ps2pdf to produce the final .pdf file.
    """
    # Extract path:
    path, texfile = os.path.split(os.path.realpath(texfile))
    # Remove extension:
    texfile, extension = os.path.splitext(texfile)

    if extension not in [".tex", ""]:
        raise ValueError("Input file does not have a .tex extension")

    if extension == "" and os.path.isfile(f"{path}/{texfile}.tex"):
        extension = ".tex"

    if not os.path.isfile(f"{path}/{texfile}.tex"):
        raise ValueError("Input .tex file does not exist")

    # Default paper format:
    if paper is None:
        paper = cm.get('paper')

    # Proceed in place:
    with u.cd(path):
        # Re-generate bib file if necessary.
        missing = build_bib(f'{texfile}.tex')

        # Clean up:
        clear_latex(texfile)

        # Compile into dvi:
        subprocess.call(['latex',  texfile], shell=False)
        subprocess.call(['bibtex', texfile], shell=False)
        subprocess.call(['latex',  texfile], shell=False)
        subprocess.call(['latex',  texfile], shell=False)

        # dvi to pdf:
        # I could actually split the dvips and ps2pdf calls to make the code
        # easier to follow, but piping the outputs actually make it faster:
        subprocess.call(
            f'dvips -R0 -P pdf -t {paper} -f {texfile} | '
             'ps2pdf -dCompatibilityLevel=1.3 -dEmbedAllFonts=true '
            f'-dMaxSubsetPct=100 -dSubsetFonts=true - - > {texfile}.pdf',
             shell=True)
        # Some notes:
        # (1) '-P pdf' makes the file to look good on screen, says STScI:
        #     http://www.stsci.edu/hst/proposing/info/how-to-make-pdf
        # (2) See 'man ps2pdf' to understand the dashes.
        # (3) See https://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDFCreationSettings_v9.pdf for ps2pdf options.

    if len(missing) > 0:
        print(f"\n{texfile}.tex has some references not found:")
        for key in missing:
            print("- " + key)


def compile_pdflatex(texfile):
    """
    Compile a .tex file into a .pdf file using pdflatex calls.

    Parameters
    ----------
    texfile: String
        Path to an existing .tex file.

    Notes
    -----
    This function executes the following calls:
    - compute a bibfile out of the citation calls in the .tex file.
    - removes all outputs from previous compilations (see clear_latex())
    - calls pdflatex, bibtex, pdflatex, pdflatex to produce a .pdf file
    """
    # Extract path:
    path, texfile = os.path.split(os.path.realpath(texfile))
    # Remove extension:
    texfile, extension = os.path.splitext(texfile)

    if extension not in [".tex", ""]:
        raise ValueError("Input file does not have a .tex extension")

    if extension == "" and os.path.isfile(f"{path}/{texfile}.tex"):
        extension = ".tex"

    if not os.path.isfile(f"{path}/{texfile}.tex"):
        raise ValueError("Input .tex file does not exist")

    # Proceed in place:
    with u.cd(path):
        # Re-generate bib file if necessary.
        missing = build_bib(f'{texfile}.tex')

        # Clean up:
        clear_latex(texfile)

        # Compile into pdf:
        subprocess.call(['pdflatex', texfile], shell=False)
        subprocess.call(['bibtex', texfile], shell=False)
        subprocess.call(['pdflatex', texfile], shell=False)
        subprocess.call(['pdflatex', texfile], shell=False)

    if len(missing) > 0:
        print(f"\n{texfile}.tex has some references not found:")
        for key in missing:
            print("- " + key)
