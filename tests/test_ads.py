# Copyright (c) 2018-2021 Patricio Cubillos.
# bibmanager is open-source software under the MIT license (see LICENSE).

import os
import pytest

import bibmanager.bib_manager as bm
import bibmanager.ads_manager as am
import bibmanager.config_manager as cm
import bibmanager.utils as u


expected_output1 = '\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mA deeper look at Jupiter\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2018Natur.555..168F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2018Natur.555..168F\x1b[0m\r\n\x1b[0m\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mThe Hunt for Planet Nine: Atmosphere, Spectra, Evolution, and\r\n    Detectability\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan J.; et al.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2016ApJ...824L..25F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2016ApJ...824L..25F\x1b[0m\r\n\x1b[0m\n'

expected_output2 = '\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mA Framework for Characterizing the Atmospheres of Low-mass Low-density\r\n    Transiting Planets\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan J.; et al.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2013ApJ...775...80F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2013ApJ...775...80F\x1b[0m\r\n\x1b[0m\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mOn the Carbon-to-oxygen Ratio Measurement in nearby Sun-like Stars:\r\n    Implications for Planet Formation and the Determination of Stellar\r\n    Abundances\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan J.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2012ApJ...747L..27F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2012ApJ...747L..27F\x1b[0m\r\n\x1b[0m\n'


def test_key_update_journal_year():
    # Case of journal does not matter:
    assert am.key_update("BeaulieuEtal2010ArXiVGJ436b", "2011ApJ...731...16B",
               "2010arXiv1007.0324B") == "BeaulieuEtal2011apjGJ436b"
    assert am.key_update("BeaulieuEtal2010arXivGJ436b", "2011ApJ...731...16B",
               "2010arXiv1007.0324B") == "BeaulieuEtal2011apjGJ436b"
    assert am.key_update("BeaulieuEtal2010arxivGJ436b", "2011ApJ...731...16B",
               "2010arXiv1007.0324B") == "BeaulieuEtal2011apjGJ436b"


def test_key_update_year():
    assert am.key_update("BeaulieuEtal2010apjGJ436b", "2011ApJ...731...16B",
               "2010arXiv1007.0324B") == "BeaulieuEtal2011apjGJ436b"
    # Year does not get updated if it does not match:
    assert am.key_update("BeaulieuEtal2009arxivGJ436b", "2011ApJ...731...16B",
               "2010arXiv1007.0324B") == "BeaulieuEtal2009apjGJ436b"


def test_key_update_journal():
    assert am.key_update("BeaulieuEtal2011arxivGJ436b", "2011ApJ...731...16B",
               "2011arXiv1007.0324B") == "BeaulieuEtal2011apjGJ436b"


def test_search(reqs, ads_entries, mock_init):
    query = 'author:"^mayor" year:1995 property:refereed'
    results, nmatch = am.search(query)
    assert nmatch == 1
    assert results == [ads_entries['mayor']]


def test_search_limit_cache(reqs, ads_entries, mock_init):
    query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    results, nmatch = am.search(query, start=0, cache_rows=2)
    # There are 26 matches:
    assert nmatch == 26
    # But requested only two entries:
    assert len(results) == 2
    assert results == [ads_entries['fortney2018'], ads_entries['fortney2016']]


def test_search_start(reqs, ads_entries, mock_init):
    query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    results, nmatch = am.search(query, start=2, cache_rows=2)
    # There are 26 matches:
    assert nmatch == 26
    # But requested only two entries:
    assert len(results) == 2
    # But results start from third match:
    assert results == [ads_entries['fortney2013'], ads_entries['fortney2012']]


def test_search_unauthorized(reqs, mock_init):
    cm.set("ads_token", "None")
    query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    with pytest.raises(ValueError, match='Unauthorized access to ADS.  '
            'Check that the ADS token is valid.'):
        results, nmatch = am.search(query)


def test_display_all(capsys, mock_init, ads_entries):
    results = [ads_entries['fortney2018'], ads_entries['fortney2016']]
    start  = 0
    index  = 0
    rows   = 2
    nmatch = 2
    am.display(results, start, index, rows, nmatch, short=True)
    captured = capsys.readouterr()
    assert captured.out == \
        expected_output1 + 'Showing entries 1--2 out of 2 matches.\n'


def test_display_first_batch(capsys, mock_init, ads_entries):
    results = [
        ads_entries['fortney2018'],
        ads_entries['fortney2016'],
        ads_entries['fortney2013'],
        ads_entries['fortney2012']]
    start  = 0
    index  = 0
    rows   = 2
    nmatch = 4
    am.display(results, start, index, rows, nmatch, short=True)
    captured = capsys.readouterr()
    assert captured.out == (
        expected_output1 +
        'Showing entries 1--2 out of 4 matches.  '
        'To show the next set, execute:\nbibm ads-search -n\n')


def test_display_second_batch(capsys, mock_init, ads_entries):
    results = [
        ads_entries['fortney2018'],
        ads_entries['fortney2016'],
        ads_entries['fortney2013'],
        ads_entries['fortney2012']]
    start  = 0
    index  = 2
    rows   = 2
    nmatch = 4
    am.display(results, start, index, rows, nmatch, short=True)
    captured = capsys.readouterr()
    assert captured.out == \
        expected_output2 + 'Showing entries 3--4 out of 4 matches.\n'


def test_display_over(capsys, mock_init, ads_entries):
    results = [
        ads_entries['fortney2018'],
        ads_entries['fortney2016'],
        ads_entries['fortney2013'],
        ads_entries['fortney2012']]
    start  = 0
    index  = 3
    rows   = 2
    nmatch = 4
    am.display(results, start, index, rows, nmatch, short=True)
    captured = capsys.readouterr()
    expected_output = '\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mOn the Carbon-to-oxygen Ratio Measurement in nearby Sun-like Stars:\r\n    Implications for Planet Formation and the Determination of Stellar\r\n    Abundances\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan J.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2012ApJ...747L..27F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2012ApJ...747L..27F\x1b[0m\r\n\x1b[0m\nShowing entries 4--4 out of 4 matches.\n'
    assert captured.out == expected_output


def test_add_bibtex_success(capsys, reqs, mock_init):
    captured = capsys.readouterr()
    bibcodes = ['1925PhDT.........1P']
    keys = ['Payne1925phdStellarAtmospheres']
    am.add_bibtex(bibcodes, keys)
    captured = capsys.readouterr()
    assert captured.out == "\nMerged 1 new entries.\n" \
                           "(Not counting updated references)\n"
    loaded_bibs = bm.load()
    assert len(loaded_bibs) == 1
    assert loaded_bibs[0].content == \
"""@PHDTHESIS{Payne1925phdStellarAtmospheres,
       author = {{Payne}, Cecilia Helena},
        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
     keywords = {Astronomy},
       school = {RADCLIFFE COLLEGE.},
         year = 1925,
        month = Jan,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""


def test_add_bibtex_none_found(reqs, mock_init):
    bibcodes = ['1925PhDT.....X...1P']
    keys = ['Payne1925phdStellarAtmospheres']
    with pytest.raises(ValueError,
            match="There were no entries found for the requested bibcodes."):
        am.add_bibtex(bibcodes, keys)


def test_add_bibtex_warning(capsys, reqs, mock_init):
    # A partially failing call will still add those that succeed:
    captured = capsys.readouterr()
    bibcodes = ['1925PhDT.....X...1P', '2018MNRAS.481.5286F']
    keys = ['Payne1925phdStellarAtmospheres', 'FolsomEtal2018mnrasHD219134']
    am.add_bibtex(bibcodes, keys)
    loaded_bibs = bm.load()
    assert len(loaded_bibs) == 1
    captured = capsys.readouterr()
    assert captured.out == """
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
Warning:

There were bibcodes unmatched or not found in ADS:
 - 1925PhDT.....X...1P

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


Merged 1 new entries.
(Not counting updated references)\n"""


def test_add_bibtex_with_tags(capsys, reqs, mock_init):
    captured = capsys.readouterr()
    bibcodes = ['1925PhDT.........1P']
    keys = ['Payne1925phdStellarAtmospheres']
    tags = [['stars']]
    am.add_bibtex(bibcodes, keys, tags=tags)
    captured = capsys.readouterr()
    assert captured.out == "\nMerged 1 new entries.\n" \
                           "(Not counting updated references)\n"
    loaded_bibs = bm.load()
    assert len(loaded_bibs) == 1
    assert repr(loaded_bibs[0]) == \
"""tags: stars
@PHDTHESIS{Payne1925phdStellarAtmospheres,
       author = {{Payne}, Cecilia Helena},
        title = "{Stellar Atmospheres; a Contribution to the Observational Study of High Temperature in the Reversing Layers of Stars.}",
     keywords = {Astronomy},
       school = {RADCLIFFE COLLEGE.},
         year = 1925,
        month = Jan,
       adsurl = {https://ui.adsabs.harvard.edu/abs/1925PhDT.........1P},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""


@pytest.mark.skip(reason="Can I test this without monkeypatching the request?")
def test_update(capsys, mock_init_sample):
    captured = capsys.readouterr()
    am.update()
    captured = capsys.readouterr()
    assert captured.out == """
Merged 0 new entries.
(Not counting updated references)

There were 1 entries updated from ArXiv to their peer-reviewed version.
These ones changed their key:
  BeaulieuEtal2010arxivGJ436b -> BeaulieuEtal2011apjGJ436b\n"""


def test_manager_none(capsys, reqs, ads_entries, mock_init):
    am.manager(None)
    captured = capsys.readouterr()
    assert captured.out == "There are no more entries for this query.\n"


def test_manager_query_no_caching(capsys, reqs, ads_entries, mock_init):
    query = 'author:"^mayor" year:1995 property:refereed'
    am.manager(query)
    captured = capsys.readouterr()
    expected_output = '\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mA Jupiter-mass companion to a solar-type star\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mMayor, Michel and Queloz, Didier\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/1995Natur.378..355M\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m1995Natur.378..355M\x1b[0m\r\n\x1b[0m\nShowing entries 1--1 out of 1 matches.\n'
    assert captured.out == expected_output


def test_manager_query_caching(capsys, reqs, ads_entries, mock_init):
    cm.set('ads_display', '2')
    captured = capsys.readouterr()
    am.search.__defaults__ = 0, 4, 'pubdate+desc'
    query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    am.manager(query)
    captured = capsys.readouterr()
    assert os.path.exists(u.BM_CACHE())
    assert captured.out == (
        expected_output1 +
        'Showing entries 1--2 out of 26 matches.  To show the next set, '
        'execute:\nbibm ads-search -n\n')


def test_manager_from_cache(capsys, reqs, ads_entries, mock_init):
    cm.set('ads_display', '2')
    captured = capsys.readouterr()
    am.search.__defaults__ = 0, 4, 'pubdate+desc'
    query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    am.manager(query)
    captured = capsys.readouterr()
    am.manager(None)
    captured = capsys.readouterr()
    assert captured.out == expected_output2 + 'Showing entries 3--4 out of 26 matches.  To show the next set, execute:\nbibm ads-search -n\n'


def test_manager_cache_trigger_search(capsys, reqs, ads_entries, mock_init):
    cm.set('ads_display', '2')
    am.search.__defaults__ = 0, 4, 'pubdate+desc'
    query = 'author:"^fortney, j" year:2000-2018 property:refereed'
    am.manager(query)
    am.manager(None)
    captured = capsys.readouterr()
    am.manager(None)
    captured = capsys.readouterr()
    expected_output = "\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mDiscovery and Atmospheric Characterization of Giant Planet Kepler-12b:\r\n    An Inflated Radius Outlier\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, Jonathan J.; et al.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2011ApJS..197....9F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2011ApJS..197....9F\x1b[0m\r\n\x1b[0m\x1b[0m\x1b[?7h\x1b[0m\r\n\x1b[0;38;5;33mTitle\x1b[0m: \x1b[0;38;5;130mSelf-consistent Model Atmospheres and the Cooling of the Solar System's\r\n    Giant Planets\x1b[0m\r\n\x1b[0;38;5;33mAuthors\x1b[0m: \x1b[0;38;5;130mFortney, J. J.; et al.\x1b[0m\r\n\x1b[0;38;5;33mADS URL\x1b[0m: \x1b[0;38;5;130mhttps://ui.adsabs.harvard.edu/abs/2011ApJ...729...32F\x1b[0m\r\n\x1b[0;38;5;33mbibcode\x1b[0m: \x1b[0;38;5;142m2011ApJ...729...32F\x1b[0m\r\n\x1b[0m\nShowing entries 5--6 out of 26 matches.  To show the next set, execute:\nbibm ads-search -n\n"
    assert captured.out == expected_output
