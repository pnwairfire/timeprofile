from setuptools import setup, find_packages

from timeprofile import __version__

test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='timeprofile',
    version=__version__,
    license='GPLv3+',
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[],
    package_data={
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/timeprofile',
    description='Package for time profiling emissions output.',
    install_requires=[
        "nested_dict",
        "pyairfire>=1.1.1"
    ],
    dependency_links=[
        "https://pypi.smoke.airfire.org/simple/pyairfire/",
    ],
    tests_require=test_requirements
)
