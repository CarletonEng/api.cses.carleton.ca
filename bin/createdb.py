#! /usr/bin/env python3

"""
Reset environment to empty with required schema.

- Delete data directory.
- Create DB schema.
"""

import _util

import os, shutil

from api import app, db

shutil.rmtree(app.config.datapath, ignore_errors=True)
app.create()

# Mark the database version.
from alembic import command
from alembic.config import Config
alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")
