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

Install following l1t-utm wheels or build l1t-utm python bindings.

 * `tmEventSetup>=0.7.3`
 * `tmTable>=0.7.3`


## Install

Install using pip

```bash
pip install https://github.com/cms-l1-globaltrigger/tm-reporter/archive/master.zip#egg=tm-reporter-2.7.0
```

Install from local source

```bash
git clone https://gitlab.cern.ch/cms-l1-globaltrigger/tm-reporter.git
cd tm-reporter
python setup.py test
python setup.py install
```
