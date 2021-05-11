XML Menu Reporter
=================

## Install

Install using pip (>= 19.0).

```bash
pip install --upgrade pip
pip install git+https://github.com/cms-l1-globaltrigger/tm-reporter.git@2.8.2
```

## Basic usage

Generate HTML/TWiki reports from XML trigger menu.

```bash
tm-reporter [-m {html,twiki}] [-o <dir>] <filename>
```

Output modes are `html` or `twiki` and defaults to `html` if not specified.

The default output location is the current working directory if not specified
other using the `-o` flag.
