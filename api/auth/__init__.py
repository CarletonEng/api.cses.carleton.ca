import random
from datetime import datetime, timedelta
from crypt import crypt
from hmac import compare_digest

import api
from api import db

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
	
	id       = db.Column("id", db.HexLong, primary_key=True)
	__pass   = db.Column("pass", db.String)
	__ctime  = db.Column("ctime", db.DateTime, default=lambda: datetime.utcnow())
	_userid  = db.Column("userid", db.ForeignKey("person.id"))
	perms    = db.Column("perms", db.JSON);
	
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
		if not api.app.config.debug:
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
		
		A self.dbs object that is a database session is required.
	"""
	@api.dbs
	def w(self, *args):
		self.req.auth = None
		ah = self.req.headers.get("Authorization")
		if ah:
			method, _, token = ah.partition(" ")
			if method == "Bearer":
				self.req.auth = Auth.fromtoken(self.dbs, token)
			
			# We don't want caches keeping requests with auth strings.
			if hasattr(self, "cache") and self.cache.type == "public":
				self.cache.type = "private"
		
		self.headers["Vary"] += ",Authorization"
		
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
			if "localhost" in self.req.host:
				self.headers["WWW-Authenticate"] = 'Bearer realm="http://localhost:1234/login"'
			elif "kevincox.ca" in self.req.host:
				self.headers["WWW-Authenticate"] = 'Bearer realm="http://cses.kevincox.ca/login"'
			else:
				self.headers["WWW-Authenticate"] = 'Bearer realm="http://cses.carleton.ca/login"'
			self.content_type = "application/json"
			self.data = '{"e":1,"msg":"Authorization required."}\n'
		else:
			return f(self, *args)
	return w
