#! /usr/bin/env python3

# Copyright 2014 Kevin Cox

################################################################################
#                                                                              #
#  This software is provided 'as-is', without any express or implied           #
#  warranty. In no event will the authors be held liable for any damages       #
#  arising from the use of this software.                                      #
#                                                                              #
#  Permission is granted to anyone to use this software for any purpose,       #
#  including commercial applications, and to alter it and redistribute it      #
#  freely, subject to the following restrictions:                              #
#                                                                              #
#  1. The origin of this software must not be misrepresented; you must not     #
#     claim that you wrote the original software. If you use this software in  #
#     a product, an acknowledgment in the product documentation would be       #
#     appreciated but is not required.                                         #
#                                                                              #
#  2. Altered source versions must be plainly marked as such, and must not be  #
#     misrepresented as being the original software.                           #
#                                                                              #
#  3. This notice may not be removed or altered from any source distribution.  #
#                                                                              #
################################################################################

import random
from datetime import datetime, timedelta
from crypt import crypt
from hmac import compare_digest

import api
import api.db as db

srand = random.SystemRandom()

class Auth(db.Base):
	""" An authorization.
		
		An authorization has an associated user and set of permissions.  An
		authorization also has a "password" that is not stored, so that if the
		database leaked the stored values could not be used to login.
		
		Class Attributes:
			AGE_MAX:
				A timedelta constant representing the maximum time for which an
				authorization is valid.
		
		Instance Attributes:
			id:
				A hex sting uniquely identifying this authorization.
			user:
				The User to which this authorization applies.
			password:
				When an authorization is created with the constructor this will
				be set to the randomly generated "password".  This value is not
				present when loaded from the database (as it is not stored) You
				probably want to use the token property to access it.
	"""
	
	__tablename__ = 'auth'
	AGE_MAX = timedelta(weeks=2)
	
	id       = db.Column(db.HexLong, primary_key=True)
	__pass   = db.Column(db.String)
	__ctime  = db.Column(db.DateTime, default=lambda: datetime.utcnow())
	__userid = db.Column(db.Hex, db.ForeignKey("person.id"))
	perms    = db.Column(db.JSON);
	
	@staticmethod
	def fromtoken(dbs, tok):
		""" Get an auth from a token.
			
			Returns:
				The appropriate Auth if the token was valid or None.
		"""
		id, _, pw = tok.partition("$")
		a = dbs.query(Auth).filter(Auth.id == id).first()
		
		if not a:
			return None
		if a.expired:
			return None
		if not a.__passcheck(pw):
			return None
		
		return a
	
	def __init__(self, user):
		""" Generates an auth with random values. """
		self.id       = format(srand.getrandbits(512), "X")
		self.password = format(srand.getrandbits(512), "X")
		self.user     = user
		self.__pass   = crypt(self.password)
	
	@property
	def token(self):
		""" Return the "token" for the auth.
			
			The token is a string that is passed to the consumer allowing them
			to use this authorization.  It contains both the identifier and the
			"password".
			
			This is only available if the auth was created with its constructor.
		"""
		return self.id+"$"+self.password
	
	def neverusethisinsecuremethod_set(self, id, pw):
		""" Set the username and password.
			This function should *NEVEREVEREVEREVEREVER* be used in production.
			You should always use the securely random values created in the
			constructor `Auth(user)`.  This function is *only* useful for
			creating repeatable test data for development.
		"""
		if not api.app.debug:
			raise Exception("Someone called this in production code.")
		
		self.id       = id
		self.password = pw
		self.__pass   = crypt(pw)
	
	@property
	def expired(self):
		""" Check if the auth has expired. """
		return datetime.utcnow() - self.__ctime > Auth.AGE_MAX
	
	def __passcheck(self, pw):
		return compare_digest(crypt(pw, self.__pass), self.__pass)
	
	def __repr__(self):
		return "Auth({}..., {})".format(self.id[:10], repr(self.user))

def auth(f):
	""" A wrapper that gets a request's authorization.
		
		This parses the Authorization header and if an auth token is provided
		converts it into an Auth.  `self.req.auth` is set to this token if valid
		otherwise it is set to None.
	"""
	def w(self, *args):
		self.req.auth = None
		ah = self.req.headers.get("Authorization")
		if ah:
			method, _, token = ah.partition(" ")
			if method == "Bearer":
				self.req.auth = Auth.fromtoken(self.dbs, token)
		
		return f(self, *args)
	return w

def authrequired(f):
	""" A wrapper to check for an auth.
		
		This parses the auth out of the request and ensures that one exists.
		If one does not exist it returns a 401 with a json response.
	"""
	@auth
	def w(self, *args):
		if not self.req.auth:
			self.status_code = 401
			return '{"e":"401","msg":"Authorization required."}'
		
		return f(self, *args)
	return w
