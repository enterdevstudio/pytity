# Contributing to pytity

## Clone the repository

First step is to clone the repository:

```bash
$ git clone git@github.com:marienfressinaud/pytity.git
```

Then, don't forget to switch to the development branch:

```bash
$ git checkout dev
```

Then you can begin to hack. Have fun!

## Generate the documentation

Documentation can be extracted from source code. You need to install Sphinx before:

```bash
$ pip install sphinx
```

Then, you'll be able to generate documentation:

```bash
$ cd doc
$ make html
```

Documentation should be available under `./doc/_build/html/index.html` now.

## Running tests

Tests require, at least, pytest. To start them, you just have to run following command:

```bash
$ python3 setup.py test
```

Pytest will find and run tests under `./tests` directory in addition of doctests in Docstrings.

## Running complete tests

I want 100% of the code to be tested (it is a hard requirement!). Most of all, I want source code PEP8-compliant. For that, please install flake8 and coverage module from Pypi:

```bash
$ pip install coverage flake8
```

Then, you could run one of my favorite command lines:

```bash
$ flake8 --max-complexity=8 pytity tests && coverage run --source pytity setup.py test && coverage report -m
```

Some explanations:

1. The first command (`flake8`) tests source code is PEP8-compliant. In addition, it will test code complexity according to the McCabe complexity. [More information on flake8](https://flake8.readthedocs.org).
2. If the previous command does not failed, we run unit tests through the coverage module in order to collect which lines are tested.
3. If tests don't failed, coverage shows a report.
