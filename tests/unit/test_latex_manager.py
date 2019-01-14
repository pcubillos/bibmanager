import os
import bibmanager.latex_manager as lm


def test_no_comments():
    assert lm.no_comments("") == ""
    assert lm.no_comments("Hello world.") == "Hello world."
    assert lm.no_comments("inline comment % comment") == "inline comment"
    assert lm.no_comments("% comment line.") == ""
    assert lm.no_comments("percentage \\%") == "percentage \\%"
    # If first line is comment, '\n' stays:
    assert lm.no_comments("% comment line.\nThen this") == "\nThen this"
    # If not, entire line is removed (including '\n'):
    assert lm.no_comments("Line\n%comment\nanother line") \
                       == "Line\nanother line"


def test_citations1():
    cites = lm.citations("\\citep{Author}.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep{\n Author }.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep[pre]{Author}.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep[pre][post]{Author}.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep\n[][]{Author}.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep [pre] [post] {Author}.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep[{\\pre},][post]{Author}.")
    assert next(cites) == "Author"
    # Outer commas are ignored:
    cites = lm.citations("\\citep{,Author,}.")
    assert next(cites) == "Author"

def test_citations2():
    # Multiple citations:
    cites = lm.citations("\\citep[{\\pre},][post]{Author1, Author2}.")
    assert next(cites) == "Author1"
    assert next(cites) == "Author2"
    cites = lm.citations(
                "\\citep[pre][post]{Author1} and \\citep[pre][post]{Author2}.")
    assert next(cites) == "Author1"
    assert next(cites) == "Author2"
    cites = lm.citations("\\citep[pre\n ][post] {Author1, Author2}")
    assert next(cites) == "Author1"
    assert next(cites) == "Author2"

def test_citations3():
    # Recursive citations:
    cites = lm.citations(
        "\\citep[see also \\citealp{Author1}][\\citealp{Author3}]{Author2}")
    assert next(cites) == "Author1"
    assert next(cites) == "Author2"
    assert next(cites) == "Author3"

def test_citations4():
    # Match all of these:
    assert next(lm.citations("\\cite{AuthorA}"))          == "AuthorA"
    assert next(lm.citations("\\nocite{AuthorB}"))        == "AuthorB"
    assert next(lm.citations("\\defcitealias{AuthorC}"))  == "AuthorC"
    assert next(lm.citations("\\citet{AuthorD}"))         == "AuthorD"
    assert next(lm.citations("\\citet*{AuthorE}"))        == "AuthorE"
    assert next(lm.citations("\\Citet{AuthorF}"))         == "AuthorF"
    assert next(lm.citations("\\Citet*{AuthorG}"))        == "AuthorG"
    assert next(lm.citations("\\citep{AuthorH}"))         == "AuthorH"
    assert next(lm.citations("\\citep*{AuthorI}"))        == "AuthorI"
    assert next(lm.citations("\\Citep{AuthorJ}"))         == "AuthorJ"
    assert next(lm.citations("\\Citep*{AuthorK}"))        == "AuthorK"
    assert next(lm.citations("\\citealt{AuthorL}"))       == "AuthorL"
    assert next(lm.citations("\\citealt*{AuthorM}"))      == "AuthorM"
    assert next(lm.citations("\\Citealt{AuthorN}"))       == "AuthorN"
    assert next(lm.citations("\\Citealt*{AuthorO}"))      == "AuthorO"
    assert next(lm.citations("\\citealp{AuthorP}"))       == "AuthorP"
    assert next(lm.citations("\\citealp*{AuthorQ}"))      == "AuthorQ"
    assert next(lm.citations("\\Citealp{AuthorR}"))       == "AuthorR"
    assert next(lm.citations("\\Citealp*{AuthorS}"))      == "AuthorS"
    assert next(lm.citations("\\citeauthor{AuthorT}"))    == "AuthorT"
    assert next(lm.citations("\\citeauthor*{AuthorU}"))   == "AuthorU"
    assert next(lm.citations("\\Citeauthor{AuthorV}"))    == "AuthorV"
    assert next(lm.citations("\\Citeauthor*{AuthorW}"))   == "AuthorW"
    assert next(lm.citations("\\citeyear{AuthorX}"))      == "AuthorX"
    assert next(lm.citations("\\citeyear*{AuthorY}"))     == "AuthorY"
    assert next(lm.citations("\\citeyearpar{AuthorZ}"))   == "AuthorZ"
    assert next(lm.citations("\\citeyearpar*{AuthorAA}")) == "AuthorAA"

def test_citations5():
    # The sample tex file:
    texfile = os.path.expanduser('~') + "/.bibmanager/examples/sample.tex"
    with open(texfile) as f:
        tex = f.read()
    tex = lm.no_comments(tex)
    cites = [citation for citation in lm.citations(tex)]
    assert cites == [
        'AASteamHendrickson2018aastex62',
        'vanderWaltEtal2011numpy',
        'JonesEtal2001scipy',
        'Hunter2007ieeeMatplotlib',
        'PerezGranger2007cseIPython',
        'MeurerEtal2017pjcsSYMPY',
        'Astropycollab2013aaAstropy',
        'AASteamHendrickson2018aastex62']


def test_build_bib():
    pass


def test_clear_latex():
    pass


def test_compile_latex():
    pass


def test_compile_pdflatex():
    pass
