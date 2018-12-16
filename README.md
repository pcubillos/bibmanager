# bibmanager
## A Manager for LaTeX Bibliographic Entries

### Features
* Unique database
* Automatic checks for invalid, duplicates, arxiv-to-journal updates
* Merge your .bib file into bibmanager
* Command-line .bib or .bbl build from your .tex files
* Command-line entry adding via your default text editor
* Command-line querry by author, year, or key
* Command-line ADS search

### Table of Contents
* [Team Members](#team-members)
* [Install](#install)
* [Getting Started](#getting-started)
* [Be Kind](#be-kind)
* [License](#license)

### Team Members
* [Patricio Cubillos](https://github.com/pcubillos/) (IWF) <patricio.cubillos@oeaw.ac.at>

### Install
``bibmanager`` is compatible with Python3 (what about Py 2?), and runs (at least) in both Linux and OSX.  
To obtain the ``bibmanager`` code, clone this repository to your local machine with the following terminal commands:  
```shell
pip install bibmananger
```

```shell
# Clone the repository to your working directory:  
git clone https://github.com/pcubillos/bibmanager/
cd bibmanager
python setup.py install
```

Follow the instructions in the ADS dev API:
https://github.com/adsabs/adsabs-dev-api

https://github.com/adsabs/adsabs-dev-api/blob/master/Converting_curl_to_python.ipynb
Make ADS querries
Get the BibTeX entry for a single bibcode


### Getting Started

TBD

```shell
# Add your bib file into the bibmanager database:
bibm merge myfile.bib

# Generate bib for Latex project:
bibm latex myproject.tex
```

### Be Kind

Please, be kind and acknowledge the effort of the developers of this project.
TBD: Get a Zenodo doi

### License

Copyright (c) 2018 Patricio Cubillos and contributors.
``bibmanager`` is open-source software under the MIT license (see LICENSE).

