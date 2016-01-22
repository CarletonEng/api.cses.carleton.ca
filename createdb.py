#! /usr/bin/env python3

import os, shutil

os.environ["CSESAPI_DEBUG"] = "TRUE"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import api
from api import app, db

shutil.rmtree(app.config.datapath, ignore_errors=True)
app.create()

# Mark the database version.
from alembic import command
from alembic.config import Config
alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")
