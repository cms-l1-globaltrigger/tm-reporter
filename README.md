VHDL Reporter
=============

## Basic usage

Generate HTML/TWiki reports from XML trigger menu.

    $ tm-reporter [-m {html,twiki}] [-o <dir>] <filename>

Output modes are `html` or `twiki` and defaults to `html` if not specified.

The default output location is the current working directory if not specified
other using the `-o` flag.

## Dependencies

 * `jinja2`
 * `tmEventSetup`

**Note:** make sure to set `UTM_ROOT` before executing.
