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

import api.framework
import api.db as db

app = framework.App()
app.config.blobs = os.path.realpath(__file__+"../../blobs")+"/"

#@TODO: Change the options http to https only.
originre = re.compile("https?://(cses\.(carleton\.ca|kevincox\.ca)|localhost)(:[0-9]+)?$")

class Handler(framework.Handler):
	""" A handler for the API.
		
		A slightly improved handler.  It only has features that add minimal
		overhead to the request.  The features are documented below.
		
		CORS:
			This function controls CORS.  By default it allows from
	"""
	def before(self):
		if (getattr(self.__class__, "origin_any", False) or
		    originre.match(self.req.headers.get("Origin", ""))):
			self.headers["Access-Control-Allow-Origin"] = self.req.headers.get("Origin", "")
		
		self.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
		self.headers["Access-Control-Allow-Headers"] = "Accept, Authorization, Content-Type"
		self.headers["Access-Control-Max-Age"]       = "31536000"
	
	def OPTIONS(self, *args):
		pass

def dbs(f):
	""" Use a database session for a handler.
		
		This sets up and tears down a database session for the handler.  This
		is exception safe.  Note that you must still manually commit, unhanded
		transactions will be rolled back.
		
		The session will be available in `self.dbs`.
	"""
	def w(self, *args):
		self.dbs = None
		try:
			self.dbs = db.Session()
			return f(self, *args)
		finally:
			if self.dbs:
				self.dbs.close()
	return w

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

def json_out(f):
	""" wrapper to format handlers output as json
		
		This takes the value returned buy the wrapped function and writes a json
		formatted version to the response.
	"""
	def w(self, *args):
		r = f(self, *args)
		self.data = json.dumps(r)+"\n"
	return w

def json_io(f):
	""" wrapper to handle json input and output
		
		This wrapper parsed a json request, returning json errors if the request
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
		self.data = json.dumps(r)+"\n"
	return w

@app.route("/")
class index(framework.Handler):
	def GET(self):
		self.headers["Cache-Control"] = "max-age=31536000,stale-while-revalidate=31536000"
		self.data = "This is the API, go away.\n"

import api.person.handler
import api.auth.handler
import api.csp.handler
import api.post.handler
