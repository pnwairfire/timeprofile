# timeprofile

This package provides a module for time profiling emissions output.

***This software is provided for research purposes only. It's output may
not accurately reflect observed data due to numerous reasons. Data are
provisional; use at own risk.***

## Python 2 and 3 Support

This package was originally developed to support python 2.7, but has since
been refactored to support 3.5. Attempts to support both 2.7 and 3.5 have
been made but are not guaranteed.

## Development

### Clone Repo

Via ssh:

    git clone git@github.com:pnwairfire/timeprofile.git

or http:

    git clone https://github.com/pnwairfire/timeprofile.git

### Install Dependencies

Run the following to install dependencies:

    pip install -r requirements.txt
    pip install -r requirements-test.txt
    pip install -r requirements-dev.txt

### Setup Environment

To import timeprofile in development, you'll have to add the repo root directory
to the search path.

## Running tests

Use pytest:

    pytest

You can also use the ```--collect-only``` option to see a list of all tests.

    pytest --collect-only

See [pytest](http://pytest.org/latest/getting-started.html#getstarted) for more information about

## Installing

### Installing With pip

TODO: ...Fill In...

First, install pip (with sudo if necessary):

    apt-get install python-pip
    pip install --upgrade pip

Then, to install, for example, v1.1.3, use the following (with sudo if necessary):

    pip install --extra-index https://pypi.airfire.org/simple timeprofile==1.1.3

If you get an error like

    AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex

it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip

## Usage

The simplest case is when the time window is a 24-hour period,
from midnight to midnight.  In this case, time profiling would yield the
following:

    ...FILL IN...

A more complicated scenario would be a time window of, say, 36 hours, starting at 6:00am on day and going until 6:00pm the following day.  Time profiling would yield the following:

    ...FILL IN...

A even more complicated scenario would be a time window of, say, 36.75 hours, starting at 6:30am on day and going until 7:15pm the following day.  Time profiling would yield the following:

    ...FILL IN...
