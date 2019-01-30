from distutils.core import setup
from tmReporter import __version__ as version

long_description = open('README.md').read()

setup(
    name="tm-reporter",
    version=version,
    url="https://github.com/cms-l1-globaltrigger/tm-reporter",
    author="Bernhard Arnold",
    author_email="bernhard.arnold@cern.ch",
    description="Generate HTML/TWiki reports from XML trigger menu.",
    long_description=long_description,
    packages=["tmReporter"],
    scripts=["scripts/tm-reporter"],
    license="GPLv3",
    keywords="",
    platforms="any",
    classifiers=[
        "Topic :: Software Development",
        "Topic :: Utilities",
    ]
)
