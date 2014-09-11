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

import re
import json
import os.path
import traceback

from api import framework
from api.config import Config

def autorepr(self, *args, **kwargs):
	leader = type(self).__name__ + "("
	a = " "*len(leader)
	
	first = [True]
	def ifnf(s):
		""" Output string if not first.
		"""
		if first[0]:
			first[0] = False
			return ""
		else:
			return s
	
	return "".join([leader] + [
		ifnf(", ")+repr(a) for a in args
	] + [
		ifnf(",\n"+a)+k+"="+repr(v) for k, v in kwargs.items()
	] + [")"])

class CSESAPI(framework.App):
	""" Our App.
		
		(And yes the name is camel case)
	"""
	def __init__(self):
		super().__init__()
		
		self.config = Config()
	
	def create(self):
		os.makedirs(self.config.datapath, 0o755, exist_ok=True)
		db.Base.metadata.create_all(db.engine)

app = CSESAPI()

#@TODO: Change the options http to https only.
originre = re.compile("https?://(cses\.(carleton\.ca|kevincox\.ca|engsoc\.org)|localhost)(:[0-9]+)?$")

class Handler(framework.Handler):
	""" A handler for the API.
		
		A slightly improved handler.  It only has features that add minimal
		overhead to the request.  The features are documented below.
		
		CORS:
			This function controls CORS.  By default it allows from selected origins.
		Error control:
			Catches and logs errors.
	"""
	def __init__(self, app, req, *args):
		try:
			super().__init__(app, req, *args)
		except:
			print("-"*60)
			print("Exception handling {} {}".format(req.method, req.path))
			traceback.print_exc()
			print("-"*60)
			
			self.status_code = 500
			self.data = '{"e":500,"msg":"Internal Server Error."}\n'
	
	def before(self):
		if (getattr(self.__class__, "origin_any", False) or
		    originre.match(self.req.headers.get("Origin", ""))):
			self.headers["Access-Control-Allow-Origin"] = self.req.headers.get("Origin", "")
		
		self.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
		self.headers["Access-Control-Allow-Headers"] = "Accept, Authorization, Content-Type"
		self.headers["Access-Control-Max-Age"]       = "31536000"
	
	def OPTIONS(self, *args):
		pass

from api import db

def dbs(f):
	""" Use a database session for a handler.
		
		This sets up and tears down a database session for the handler.  This
		is exception safe.  Note that you must still manually commit, unhanded
		transactions will be rolled back.
		
		The session will be available in `self.dbs`.
	"""
	def w(self, *args):
		if hasattr(self, "dbs"):
			return f(self, *args)
		
		self.dbs = None
		try:
			self.dbs = db.Session()
			return f(self, *args)
		finally:
			if self.dbs:
				self.dbs.close()
	return w

def dbfetch(klass, arg=1):
	arg -= 1
	def d(f):
		@dbs
		def w(self, *args):
			args = list(args)
			try:
				args[arg] = self.dbs.query(klass).get(args[arg-1])
			except db.StatementError as e:
				self.status_code = 400
				self.content_type = "application/json; charset=utf-8"
				self.data = '{"e":1,"msg":"Invalid ID"}\n'
				return
			
			if not args[arg]:
				self.status_code = 404
				self.content_type = "application/json; charset=utf-8"
				self.data = '{"e":1,"msg":"Item does not exist."}\n'
				return
			
			return f(self, *args)
		return w
	return d

def json_in(f):
	""" wrapper to parse json input.
		
		This function attempts to read json import for the request body.
		`self.req.json` is set to the parsed json if present, otherwise null.
	"""
	def w(self, *args):
		self.max_content_length = 4*1024*1024
		
		self.req.json = None
		if self.req.mimetype != "application/json":
			try:
				self.req.json = json.loads(self.req.get_data(as_text=True))
			except: pass
		
		f(self, *args)
	return w

def tojson(o):
	if app.config.debug:
		j = json.dumps(o, indent="\t")
	else:
		j = json.dumps(o, separators=(",",":"))
	
	j = j+"\n"
	
	if app.config.debug:
		print(j)
		
	return j

def json_out(f):
	""" wrapper to format handlers output as json
		
		This takes the value returned buy the wrapped function and writes a json
		formatted version to the response.
	"""
	def w(self, *args):
		r = f(self, *args)
		self.content_type = "application/json"
		self.data = tojson(r)
	return w

def json_io(f):
	""" wrapper to handle json input and output
		
		This wrapper parses a json request, returning json errors if the request
		doesn't contain json.  The parsed json object is then put in
		`self.req.json` and the wrapped function is called.  The return value
		of said function is then formatted as json and written to the response.
	"""
	def w(self, *args):
		if self.req.mimetype != "application/json":
			self.status_code = 400
			self.data = '{"e":1,"msg":"Content-Type must be application/json."}\n'
			return
		
		try:
			self.req.json = json.loads(self.req.get_data(as_text=True))
		except:
			self.status_code = 400
			self.data = '{"e":1,"msg":"JSON request body required."}\n'
			return
		
		r = f(self, *args)
		self.content_type = "application/json; charset=utf-8"
		self.data = tojson(r)
	return w

class CacheOptions:
	def __init__(self, sec, stale=None, error=None, type="public"):
		self.seconds = sec
		self.stale   = stale
		self.error   = error
		self.type    = type
		self.more    = []
	def __str__(self):
		r = [self.type, "max-age="+str(self.seconds)]
		
		if self.stale is not None:
			r.append("stale-while-revalidate="+str(self.stale))
		if self.error is not None:
			r.append("stale-if-error="+str(self.error))
		r.extend(self.more)
		
		return ",".join(r)

def cache(sec, *cacheargs, **cachekwargs):
	""" Wrapper to set cache parameters.
	"""
	
	def d(f):
		def w(self, *args):
			self.cache = CacheOptions(sec, *cacheargs, **cachekwargs)
			
			r = f(self, *args)
			
			# Don't cache when debugging.
			if app.config.debug:
				self.headers["Cache-Control"] = "no-cache"
			else:
				self.headers["Cache-Control"] = str(self.cache)
				if self.cache.type == "no-cache" or self.cache.type == "no-store":
					self.headers["Pragma"] = "no-cache"
			
			return r
		return w
	return d

cachenocache = cache(0, type="no-cache")
cachenostore = cache(0, type="no-store")
cachemin     = cache(60*3, 60, 60*15)
cachehour    = cache(3600, 3600, 3600*4)
cacheday     = cache(3600*24, 3600*3, 3600*24)
cacheforever = cache(3600*365, 3600*365, 3600*365)

@app.route("/")
class index(framework.Handler):
	@cacheforever
	def GET(self):
		self.content_type = "text/plain; charset=utf-8"
		self.data = "This is the API, go away.\n"

class Default(Handler):
	@json_out
	@cachehour
	def default(self):
		self.status_code = 404
		return {"e": 404,
			"msg": "The requested URL {} is not part of the API.".format(self.req.path),
		}
app.catchall = Default

import api.auth.handler

import api.banner.handler
import api.blob.handler
import api.csp.handler
import api.person.handler
import api.post.handler
import api.tbtbook.handler

# Force evaluation of relationships.
from api.person import Person
Person()
