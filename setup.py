from setuptools import setup, find_packages

long_description = open('README.md').read()

setup(
    name='tm-reporter',
    version='2.7.1',
    url="https://github.com/cms-l1-globaltrigger/tm-reporter",
    author="Bernhard Arnold",
    author_email="bernhard.arnold@cern.ch",
    description="Generate HTML/TWiki reports from XML trigger menu.",
    long_description=long_description,
    packages=['tmReporter'],
    package_data={
        'tmReporter': [
            'templates/*.*',
        ],
    },
    install_requires=[
        'Jinja2',
        'tm-table>=0.7.3',
        'tm-eventsetup>=0.7.3',
    ],
    entry_points={
        'console_scripts': [
            'tm-reporter = tmReporter.__main__:main',
        ],
    },
    test_suite='tests',
    license='GPLv3',
    keywords="",
    platforms="any",
    classifiers=[
        "Topic :: Software Development",
        "Topic :: Utilities",
    ]
)
