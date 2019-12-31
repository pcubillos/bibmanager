# Copyright (c) 2018-2020 Patricio Cubillos and contributors.
# bibmanager is open-source software under the MIT license (see LICENSE).

import bibmanager.bib_manager as bm
import bibmanager.pdf_manager as pm


def test_guess_name_no_bibcode():
    bib = bm.Bib('''@ARTICLE{Raftery1995BIC,
       author = {{Raftery}, A.~E},
        title = "{Bayesian Model Selection in Social Research}",
         year = 1995,
    }''')
    assert pm.guess_name(bib) == 'Raftery1995.pdf'


def test_guess_name_with_bibcode():
    bib = bm.Bib('''@ARTICLE{FortneyEtal2008apjTwoClasses,
           author = {{Fortney}, J.~J. and {Lodders}, K. and {Marley}, M.~S. and
             {Freedman}, R.~S.},
            title = "{A Unified Theory for the Atmospheres of the Hot and Very Hot Jupiters: Two Classes of Irradiated Atmospheres}",
             year = "2008",
           adsurl = {https://ui.adsabs.harvard.edu/abs/2008ApJ...678.1419F},
    }''')
    assert pm.guess_name(bib) == 'Fortney2008_ApJ_678_1419.pdf'


def test_guess_name_arxiv_query():
    bib = bm.Bib('''@ARTICLE{FortneyEtal2008apjTwoClasses,
           author = {{Fortney}, J.~J. and {Lodders}, K. and {Marley}, M.~S. and
             {Freedman}, R.~S.},
            title = "{A Unified Theory for the Atmospheres of the Hot and Very Hot Jupiters: Two Classes of Irradiated Atmospheres}",
             year = "2008",
           adsurl = {https://ui.adsabs.harvard.edu/abs/2008ApJ...678.1419F},
    }''')
    assert pm.guess_name(bib, query='http://blah/EPRINT') == \
        'Fortney2008_arxiv_ApJ_678_1419.pdf'


def test_guess_name_blanks():
    bib = bm.Bib('''@MISC{AASteamHendrickson2018aastex62,
           author = {{AAS Journals Team}, and {Hendrickson}, Amy},
            title = "{Aasjournals/Aastex60: Version 6.2 Official Release}",
             year = "2018",
           adsurl = {https://ui.adsabs.harvard.edu/abs/2018zndo...1209290T},
    }''')
    assert pm.guess_name(bib) == 'AASJournalsTeam2018_zndo_12_9290.pdf'


def test_guess_name_non_letter_characters():
    bib = bm.Bib(r'''@ARTICLE{GarciaMunoz2007pssHD209458bAeronomy,
           author = {{Garc{\'\i}a-Mu{\~n}oz}, A.},
            title = "{Physical and chemical aeronomy of HD 209458b}",
             year = "2007",
           adsurl = {https://ui.adsabs.harvard.edu/abs/2007P&SS...55.1426G},
    }''')
    assert pm.guess_name(bib) == 'GarciaMunoz2007_PSS_55_1426.pdf'


def test_guess_name_non_ascii():
    bib = bm.Bib('''@ARTICLE{HuangEtal2014jqsrtCO2,
      author = {{Huang (黄新川)}, Xinchuan and {Gamache}, Robert R.},
       title = "{Reliable infrared line lists for 13 CO$_{2}$}",
        year = "2014",
      adsurl = {https://ui.adsabs.harvard.edu/abs/2014JQSRT.147..134H},
    }''')
    assert pm.guess_name(bib) == 'Huang2014_JQSRT_147_134.pdf'


def test_guess_name_bibcode_no_volume():
    bib = bm.Bib('''@PHDTHESIS{Payne1925phdStellarAtmospheres,
           author = {{Payne}, Cecilia Helena},
            title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
             year = "1925",
           adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
    }''')
    assert pm.guess_name(bib) == 'Payne1925_PhDT_1.pdf'


def test_guess_name_bibcode_no_pages():
    bib = bm.Bib('''@BOOK{Chase1986jttJANAF,
           author = {{Chase}, M.~W.},
            title = "{JANAF thermochemical tables}",
             year = "1986",
           adsurl = {https://ui.adsabs.harvard.edu/abs/1986jtt..book.....C},
    }''')
    assert pm.guess_name(bib) == 'Chase1986_jtt_book.pdf'

