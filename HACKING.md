# Hacking
## Getting it running.

The API is written in Python 3 using the Werkzeug WSGI tools and SqlAlchemy
for SQL ORM.

Both of these libraries can be installed via `easy_install` once you have python
3.  The following command should do it.

	easy_install werkzeug sqlalchemy

Once you have those set up you should be able to run `python main.py` and the
API should start on http://localhost:8080.  Typing that in your URL bar should
show you a message.

Congratulations.  You have the API up and running.

## Directory layout.

The directory layout matches the URL patterns.  For example `/auth/*` goes in
the `auth/` directory.  The actual http API components go in `api.py` in that
directory and the internal python API go in the `__init__.py` file.
