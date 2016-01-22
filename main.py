#! /usr/bin/env python3

# This script starts a development server.

import os, sys

if __name__ == "__main__":
	os.environ["CSESAPI_DEBUG"] = "TRUE"
	
	bind = sys.argv[1] if len(sys.argv) > 1 else "localhost"
	
	from api import app
	app.create()
	app.devserver(host=bind)
