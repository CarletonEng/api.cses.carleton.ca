#! /bin/bash

# Run the full suite of tests and checks.

set -ex

py.test -vvvvv --random --strict --durations=10 "$@"
