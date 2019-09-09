#!/usr/bin/env python

import argparse
import logging
import sys, os

import tmEventSetup
import tmTable

from .reporter import Reporter
from . import __version__

# Exit states
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Package directories
RootDir = os.path.dirname(__file__)
TemplatesDir = os.path.join(RootDir, 'templates')

# Available output Modes
ModeHtml = 'html'
ModeTwiki = 'twiki'
Modes = [ModeHtml, ModeTwiki]

def load_eventsetup(filename):
    """Load event setup and extend by original raw cuts from XML menu.
    How to use extension:
    >>> cut = eventSetup._cuts['MU-QLTY_HQ']
    >>> print(cut['minimum'], cut['maximum'])
    """
    # Load raw XML menu
    menu = tmTable.Menu()
    scale = tmTable.Scale()
    extSignal = tmTable.ExtSignal()
    warnings = tmTable.xml2menu(filename, menu, scale, extSignal)
    if warnings:
        raise RuntimeError(warnings)
    # Load event setup
    eventSetup = tmEventSetup.getTriggerMenu(filename)
    # HACK Extend event setup with external signals set
    eventSetup._externals_set = extSignal.extSignalSet['name']
    # HACK Extend event setup with original algorithms.
    eventSetup._algorithms = dict([(algorithm['name'], algorithm) for algorithm in menu.algorithms])
    # HACK Extend event setup with original raw cuts.
    eventSetup._cuts = {}
    for cuts in menu.cuts.values():
        for cut in cuts:
            name = cut['name']
            if name in eventSetup._cuts:
                if eventSetup._cuts[name].items() != cut.items():
                    raise RuntimeError("cuts of same name must contain same attributes")
            eventSetup._cuts[name] = cut
    return eventSetup

def parse():
    """Parse command line options."""
    parser = argparse.ArgumentParser(
        prog='tm-reporter',
        description="Level-1 Trigger Menu Reporter for XML menus.",
        epilog="Report bugs to <bernhard.arnold@cern.ch>"
    )
    parser.add_argument('filename',
        type=os.path.abspath,
        help="XML menu file to be loaded"
    )
    parser.add_argument('-m', '--mode',
        default=ModeHtml,
        choices=Modes,
        help="select output mode, default is `html')"
    )
    parser.add_argument('-o', '--outdir',
        default=os.getcwd(),
        type=os.path.abspath,
        help="target directory to write output, default is current directory"
    )
    parser.add_argument('--version',
        action='version',
        version="Reporter for Level-1 Trigger Menus version {0}".format(__version__),
    )
    return parser.parse_args()

def main():
    """Main routine."""
    args = parse()

    # Setup console logging
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    try:
        # Load XML menu and write report.
        logging.info("loading XML menu %s", args.filename)
        eventSetup = load_eventsetup(args.filename)

        logging.info("generating menu documentation...")
        reporter = Reporter(TemplatesDir, eventSetup)
        basename = eventSetup.getName()

        # Generate HTML output
        if args.mode == ModeHtml:
            filename = os.path.join(args.outdir, '{basename}.html'.format(**locals()))
            logging.info("writing HTML documentation %s", filename)
            reporter.write_html(filename)

        # Generate TWIKI output
        if args.mode == ModeTwiki:
            filename = os.path.join(args.outdir, '{basename}.twiki'.format(**locals()))
            logging.info("writing TWIKI page template %s", filename)
            reporter.write_twiki(filename)

        logging.info("done.")

    except RuntimeError as message:
        logging.error(message)
        return EXIT_FAILURE

    return EXIT_SUCCESS

if __name__ == '__main__':
    sys.exit(main())
