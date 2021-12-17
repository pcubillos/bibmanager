# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import pytest
import pathlib

import numpy as np
from conftest import cd

import bibmanager.utils as u
import bibmanager.bib_manager   as bm
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
        'HarrisEtal2020natNumpy',
        'VirtanenEtal2020natmeScipy',
        'Hunter2007ieeeMatplotlib',
        'PerezGranger2007cseIPython',
        'MeurerEtal2017pjcsSYMPY',
        'Astropycollab2013aaAstropy',
        'AASteamHendrickson2018aastex62',
        'Cubillos2019zndoBibmanager',
    ]


def test_parse_subtex_files(tmp_path):
    os.chdir(tmp_path)
    os.mkdir('dir1')
    os.mkdir('dir1/dir2')
    subfile1 = f'{tmp_path}/subfile1.tex'
    subfile2 = f'{tmp_path}/dir1/subfile2.tex'
    subfileB = f'{tmp_path}/dir1/subfileB.tex'
    subfileC = f'{tmp_path}/dir1/dir2/subfileC.tex'
    subtex1 = "This is subfile 1\n\\include{dir1/subfile2}\n"
    subtex2 = "This is subfile 2\n%\\input{dir1/subfileB}\n"
    subtexB = "This is subfile B\n\\subfile{dir1/dir2/subfileC}\n"
    subtexC = "This is subfile C\n"
    with open(subfile1, 'w') as f:
        f.write(subtex1)
    with open(subfile2, 'w') as f:
        f.write(subtex2)
    with open(subfileB, 'w') as f:
        f.write(subtexB)
    with open(subfileC, 'w') as f:
        f.write(subtexC)

    tex = r"""
\begin{document}

\input{subfile1}
\include{dir1/subfileB}

\bibliography{rate}
\end{document}
"""
    parsed = lm.parse_subtex_files(tex)
    assert parsed == tex + subtex1 + subtex2[:subtex2.index('%')] \
                     + subtexB + subtexC


def test_build_bib_inplace(mock_init):
    bm.merge(u.HOME+"examples/sample.bib")
    with cd(u.HOME+'examples'):
        missing = lm.build_bib("sample.tex")
        files = os.listdir(".")
        assert "texsample.bib" in files
        # Now check content:
        np.testing.assert_array_equal(missing, np.zeros(0,dtype="U"))
        bibs = bm.read_file("texsample.bib")
        assert len(bibs) == 8
        keys = [bib.key for bib in bibs]
        assert "AASteamHendrickson2018aastex62" in keys
        assert "HarrisEtal2020natNumpy" in keys
        assert "VirtanenEtal2020natmeScipy" in keys
        assert "Hunter2007ieeeMatplotlib" in keys
        assert "PerezGranger2007cseIPython" in keys
        assert "MeurerEtal2017pjcsSYMPY" in keys
        assert "Astropycollab2013aaAstropy" in keys
        assert "Cubillos2019zndoBibmanager" in keys


def test_build_bib_remote(mock_init):
    bm.merge(u.HOME+"examples/sample.bib")
    lm.build_bib(u.HOME+"examples/sample.tex")
    files = os.listdir(u.HOME+"examples/")
    assert "texsample.bib" in files


def test_build_bib_user_bibfile(tmp_path, mock_init):
    bibfile = f'{tmp_path}/my_file.bib'
    bm.merge(u.HOME+"examples/sample.bib")
    lm.build_bib(u.HOME+"examples/sample.tex", bibfile=bibfile)
    assert "my_file.bib" in os.listdir(str(tmp_path))


def test_build_bib_missing(capsys, tmp_path, mock_init):
    # Assert screen output:
    bibfile = f'{tmp_path}/my_file.bib'
    bm.merge(u.HOME+"examples/sample.bib")
    captured = capsys.readouterr()
    texfile = u.HOME+"examples/mock_file.tex"
    with open(texfile, "w") as f:
        f.write("\\cite{Astropycollab2013aaAstropy} \\cite{MissingEtal2019}.\n")
    missing = lm.build_bib(texfile, bibfile)
    captured = capsys.readouterr()
    assert captured.out == "References not found:\nMissingEtal2019\n"
    # Check content:
    np.testing.assert_array_equal(missing, np.array(["MissingEtal2019"]))
    bibs = bm.read_file(bibfile)
    assert len(bibs) == 1
    assert "Astropycollab2013aaAstropy" in bibs[0].key


def test_build_raise(mock_init):
    bm.merge(u.HOME+"examples/sample.bib")
    with open(u.HOME+"examples/mock_file.tex", "w") as f:
        f.write("\\cite{Astropycollab2013aaAstropy}")
    with pytest.raises(Exception,
             match="No 'bibiliography' call found in tex file."):
        lm.build_bib(u.HOME+"examples/mock_file.tex")


def test_clear_latex(mock_init):
    # Mock some 'latex output' files:
    pathlib.Path(u.HOME+"examples/sample.pdf").touch()
    pathlib.Path(u.HOME+"examples/sample.ps").touch()
    pathlib.Path(u.HOME+"examples/sample.bbl").touch()
    pathlib.Path(u.HOME+"examples/sample.dvi").touch()
    pathlib.Path(u.HOME+"examples/sample.out").touch()
    pathlib.Path(u.HOME+"examples/sample.blg").touch()
    pathlib.Path(u.HOME+"examples/sample.log").touch()
    pathlib.Path(u.HOME+"examples/sample.aux").touch()
    pathlib.Path(u.HOME+"examples/sample.lof").touch()
    pathlib.Path(u.HOME+"examples/sample.lot").touch()
    pathlib.Path(u.HOME+"examples/sample.toc").touch()
    pathlib.Path(u.HOME+"examples/sampleNotes.bib").touch()
    # Here they are:
    files = os.listdir(u.HOME+"examples")
    assert len(files) == 17
    lm.clear_latex(u.HOME+"examples/sample.tex")
    # Now they are gone:
    files = os.listdir(u.HOME+"examples")
    assert set(files) \
        == set(['aastex62.cls', 'apj_hyperref.bst', 'sample.bib', 'sample.tex',
                'top-apj.tex'])

@pytest.mark.skip(reason="Need to either mock latex, bibtex, dvi2df calls or learn how to enable them in travis CI")
def test_compile_latex():
    # Either mock heavily the latex, bibtex, dvi-pdf calls or learn how
    # to integrate them to CI.
    pass


def test_compile_latex_bad_extension(mock_init):
    with pytest.raises(ValueError,
             match="Input file does not have a .tex extension"):
        lm.compile_latex("mock_file.tecs")


def test_compile_latex_no_extension_not_found(mock_init):
    with pytest.raises(ValueError,
             match="Input .tex file does not exist"):
        lm.compile_latex("mock_file")


@pytest.mark.skip(reason="Need to either mock pdflatex and bibtex calls or learn how to enable them in travis CI")
def test_compile_pdflatex():
    # Same as test_compile_latex.
    pass


def test_compile_pdflatex_bad_extension(mock_init):
    with pytest.raises(ValueError,
             match="Input file does not have a .tex extension"):
        lm.compile_pdflatex("mock_file.tecs")


def test_compile_pdflatex_no_extension_not_found(mock_init):
    with pytest.raises(ValueError,
             match="Input .tex file does not exist"):
        lm.compile_latex("mock_file")

