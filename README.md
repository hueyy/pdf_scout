# pdf-bookmarker

This CLI tool automatically generates PDF bookmarks (also known as an 'outline' or a 'table of contents') for computer-generated PDF documents.

```bash
cd pdf-bookmarker
poetry install
poetry run python ./src/app.py
```

![screenshot](./assets/screenshot.png)

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
