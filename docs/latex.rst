.. _latex:

LaTeX Management
================

bibtex
------

Generate a bibtex file from a tex file.

**Usage**

.. code-block:: shell

  bibm bibtex [-h] texfile [bibfile]

**Description**

This command generates a BibTeX file by searching for the citation
keys in the input LaTeX file, and stores the output into BibTeX file,
named after the argument in the `\\bibliography{bib_file}` call in the
LaTeX file.  Alternatively, the user can specify the name of the
output BibTeX file with the ``bibfile`` argument.

Any citation key not found in the bibmanager database, will be
shown on the screen prompt.

**Options**

| **texfile**
|       Path to an existing LaTeX file.
|
| **bibfile**
|       Path to an output BibTeX file.
|
| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. code-block:: shell

  # Generate a BibTeX file with references cited in my_file.tex:
  bibm bibtex my_file.tex

  # Generate a BibTeX file with references cited in my_file.tex,
  # naming the output file 'this_file.bib':
  bibm bibtex my_file.tex this_file.bib

----------------------------------------------------------------------

latex
-----

Compile a LaTeX file with the latex command.

**Usage**

.. code-block:: shell

  bibm latex [-h] texfile [paper]

**Description**

This command compiles a LaTeX file using the latex command,
executing the following calls:

- Compute a BibTex file out of the citation calls in the .tex file.
- Remove all outputs from previous compilations.
- Call latex, bibtex, latex, latex to produce a .dvi file.
- Call dvi2ps and ps2pdf to produce the final .pdf file.

Prefer this command over the :code:`bibm pdflatex` command when the LaTeX file
contains .ps or .eps figures (as opposed to .pdf, .png, or .jpeg).

Note that the user does not necessarily need to be in the dir
where the LaTeX files are.

**Options**

| **texfile**
|       Path to an existing LaTeX file.
|
| **paper**
|       Paper format, e.g., letter or A4 (default=letter).
|
| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. code-block:: shell

  # Compile a LaTeX project:
  bibm latex my_file.tex

  # File extension can be ommited:
  bibm latex my_file

  # Compile, setting explicitely the output paper format:
  bibm latex my_file A4

----------------------------------------------------------------------

pdflatex
--------

Compile a LaTeX file with the pdflatex command.

**Usage**

.. code-block:: shell

  bibm pdflatex [-h] texfile

**Description**

This command compiles a LaTeX file using the pdflatex command,
executing the following calls:

- Compute a BibTeX file out of the citation calls in the LaTeX file.
- Remove all outputs from previous compilations.
- Call pdflatex, bibtex, pdflatex, pdflatex to produce a .pdf file.

Prefer this command over the :code:`bibm latex` command when the LaTeX file
contains .pdf, .png, or .jpeg figures (as opposed to .ps or .eps).

Note that the user does not necessarily need to be in the dir
where the LaTeX files are.

**Options**

| **texfile**
|       Path to an existing LaTeX file.
|
| **-h, -\\-help**
|       Show this help message and exit.

**Examples**

.. code-block:: shell

  # Compile a LaTeX project:
  bibm pdflatex my_file.tex

  # File extension can be ommited:
  bibm pdflatex my_file

