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
from datetime import datetime

import werkzeug.wrappers
import webob

class Handler(werkzeug.wrappers.Response):
	""" A framework for handling requests.
		
		This class will be instantiated for a request.  In order to modify the
		handling you should derive this class and override some methods.
		
		When a request is being handled the following sequence of calls will
		be made.
		- The before() function will be called.
		- The METHOD() function will be called, where METHOD is the http method
		  used in the request.  The function name will be all upper case.  If
		  this function doesn't exist the default() function is called instead.
		  The called function receives the request parameters captured from the
		  request path.
		- The after() function will be called with the return value of the
		  METHOD() call.
		
		It is important to notice that the dynamic calls only call all upper
		case functions, therefore all functions and properties you don't want to
		be called from outside must have at least one lowercase character.
	"""
	def __init__(self, app, req, *args):
		""" Handle the request.
			
			This sets up the class variables and then calls the handler
			functions.
		"""
		super().__init__()
		
		self.app = app
		self.req = req
		
		self.before()
		f = getattr(self, self.req.method.upper(), self.default)
		r = f(*args)
		self.after(r)
	
	def before(self):
		""" Setup
			
			This function is called before the request is handled.  This method
			should call super().before().
		"""
		pass
	
	def after(self, *args):
		""" Tear down
			
			This function is called after the request is handled and is passed
			the values returned from the called function.
			
			This function should call its super method.
		"""
		pass
	
	def default(self, *args):
		""" The default handler.
			
			This method is called if no method with the name matching the
			request method is found.  The default implementation returns a text
			error message and a 405 method not allowed error message.
			
			It is not required to call super in this method.
		"""
		self.status_code = 405
		self.content_type = "text/plain; charset=utf-8"
		self.data = "Method {} not allowed.\n".format(self.req.method)

class DefaultRoute(Handler):
	""" A default default route handler.
		
		This implementation returns a 404 not found error with a text message.
	"""
	def default(self):
		self.status_code = 404
		self.content_type = "text/plain; charset=utf-8"
		self.data = "Requested URL '{}' does not exist.\n".format(self.req.path)

class App:
	""" A WSGI Application.
		
		This is a simple WSGI framework.  It provides you with slightly more
		than nothing.
		
		This app takes a list of callables and matching regular expressions.  It
		attempts to match the regex  on each route in order and if a match is
		made the handler is called with the app, the request object, and then
		the regex capture groups as positional arguments.
		
		The handler must return a WSGI application that will be used to satisfy
		the request.
	"""
	def __init__(self):
		self.__routes = []
		self.catchall = DefaultRoute
		self.config = lambda:None
	
	def route(self, regex):
		""" A route decorator.
			
			This is a decorator is used to add a route to the handler.  The
			regex parameter is attempted against the whole path (no '$' suffix
			required) and any capture groups are passed to the handler.
		"""
		regex = re.compile(regex+"$")
		def decorator(klass):
			self.__routes.append((regex, klass))
			return klass # Pass it through.
		return decorator
	
	def __call__(self, environ, start_response):
		req = webob.Request(environ)
		responder = self.catchall
		args = []
		
		for regex, handler in self.__routes:
			match = regex.match(req.path)
			if match:
				args = match.groups()
				responder = handler
				break
		
		return responder(self, req, *args)(environ, start_response)
	
	def devserver(self, host="localhost", port=8080, debugger=True, reloader=True):
		""" Start a development HTTP server.
			
			This starts the server with debugging enabled.  This method must not
			be used in production.
			
			This method blocks forever.
		"""
		self.debug = True
		
		from werkzeug.serving import run_simple
		run_simple(host, port, self, use_debugger=debugger,
		                             use_reloader=reloader,
		                             threaded=True)
