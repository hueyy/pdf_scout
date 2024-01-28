# pdf_scout


![PyPI](https://img.shields.io/pypi/v/pdf_scout)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pdf_scout)
![PyPI - License](https://img.shields.io/pypi/l/pdf_scout)

This CLI tool automatically generates PDF bookmarks (also known as an 'outline' or a 'table of contents') for computer-generated PDF documents.

You can install it globally via pip:

```
pip install --user pdf_scout
pdf_scout ./my_document.pdf

pip uninstall pdf_scout
```

![screenshot](./assets/screenshot.png)

This project is a work in progress and will likely only generate suitable bookmarks for documents that conform to the following requirements:

* Single column of text (not multiple columns)
* Font size of header text > font size of body text
* Header text is justified or left-aligned
* Paragraph spacing for headers > body text paragraph spacing
* Consistent left margins on every page

## Supported document types

`pdf_scout` expressly seeks to supports the following classes of documents:

- Singapore State Court and Supreme Court Judgments (unreported)
- Singapore Law Reports
- ~~[OpenDoc](https://www.opendoc.gov.sg/)-generated PDFs, such as the [State Court Practice Directions 2021](https://epd-statecourts-2021.opendoc.gov.sg/) and the [Supreme Court Practice Directions 2021](https://epd-supcourt-2021.opendoc.gov.sg/)~~ – OpenDoc has been deprecated by GovTech

It may support other types of documents as well. If a particular class of document isn't supported or does not work well, please open an issue and I will consider adding support for it.

## Development

This project manages its dependencies using [poetry](https://python-poetry.org) and is only supported for Python ^3.9. After installing poetry and entering the project folder, run the following to install the dependencies:

```bash
poetry install
```

To open a virtualenv in the project folder with the dependencies, run:

```bash
poetry shell
```

To run a script directly, run:

```bash
poetry run python ./pdf_scout/app.py <INPUT_FILE_PATH>
```

Debugging using VSCode:

```bash
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client ./pdf_scout/app.py
```

### Tests

There are snapshot tests. Input PDFs are not provided at the moment, so you will have to populate the `/pdf` folder manually using the relevant sources (you may want to consider using [Clerkent](https://clerkent.huey.xyz) to download the unreported versions of judgments):

```bash
poetry run pytest
poetry run pytest --snapshot-update
```

### Static type-checking

```bash
poetry run mypy pdf_scout/app.py
```

### Tips

- Processing a large PDF can take some time, so to iterate faster when debugging certain behaviour, extract the problematic part of the PDF as a separate file

