# pdf_scout

This CLI tool automatically generates PDF bookmarks (also known as an 'outline' or a 'table of contents') for computer-generated PDF documents.

You can install it globally via pip:

```
pip install pdf_scout
pdf_scout ./my_document.pdf
pip uninstall pdf_scout
```

![screenshot](./assets/screenshot.png)

This project is a work in progress and will likely only generate accurate bookmarks for documents that conform to the following requirements:

* Single column of text (not multiple columns)
* Font size of header text >= font size of body text
* Header text is justified or left-aligned

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
poetry run python ./src/app.py
```

### Tests

There are snapshot tests. Input PDFs are not provided at the moment, so you will have to populate the `/pdf` folder manually:

```bash
poetry run pytest
poetry run pytest --snapshot-update
```