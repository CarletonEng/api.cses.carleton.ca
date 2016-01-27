#! /usr/bin/env python3

"""
This script starts a development server.
"""

import _util

import os, sys

bind = sys.argv[1] if len(sys.argv) > 1 else "localhost"

from api import app
app.create()
app.devserver(host=bind)
