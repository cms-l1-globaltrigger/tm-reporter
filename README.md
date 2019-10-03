XML Menu Reporter
=================

## Basic usage

Generate HTML/TWiki reports from XML trigger menu.

```bash
tm-reporter [-m {html,twiki}] [-o <dir>] <filename>
```

Output modes are `html` or `twiki` and defaults to `html` if not specified.

The default output location is the current working directory if not specified
other using the `-o` flag.

## Dependencies

Install following utm wheels or build utm python bindings.

 * [`tm-eventsetup>=0.7.3`](https://github.com/cms-l1-globaltrigger/tm-eventsetup)
 * [`tm-table>=0.7.3`](https://github.com/cms-l1-globaltrigger/tm-table)


## Install

Install using pip

```bash
pip install git+https://github.com/cms-l1-globaltrigger/tm-reporter.git@2.7.1
```

Install from local source

```bash
git clone https://gitlab.cern.ch/cms-l1-globaltrigger/tm-reporter.git
cd tm-reporter
python setup.py install
```
