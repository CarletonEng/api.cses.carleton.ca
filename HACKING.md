# Hacking
## Getting it running.

The API is written in Python 3 using the Werkzeug WSGI tools and SQLAlchemy
for SQL ORM.

Both of these libraries can be installed via `pip` once you have python
3.  The following command should do it.

	pip3 install -r requirements-dev.txt

Once you have those set up you should be able to run `python3 bin/server.py`
and the API should start on http://localhost:8080.  Typing that in your URL
bar should show you a message.

Congratulations.  You have the API up and running.

## Sample Data

You can load some sample data into the server by running `python3 bin/gensampledata.py`.

Pro tip: The sample data includes an admin user with id `1` and password `passwd`.

## Directory layout.

The directory layout matches the URL patterns.  For example `/auth/*` goes in
the `auth/` directory.  The actual HTTP API components go in `handler.py` in
that directory and the internal Python API go in the `__init__.py` file.
