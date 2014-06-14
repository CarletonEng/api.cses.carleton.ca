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

from urllib.parse import parse_qs

from werkzeug.wsgi import wrap_file

import api
from api import db
from api.auth import auth
from api.blob import Blob

@api.app.route("/blob")
class index(api.Handler):
	@api.dbs
	@auth
	@api.json_out
	def POST(self):
		if not "upload" in self.req.auth.perms:
			return {"e":1, "msg": "You can't upload."}
		
		pass

@api.app.route("/blob/(.*)")
def blob(app, req, id):
	def wsgi(env, start_response):
		sess = db.Session()
		try:
			b = sess.query(Blob).get(id)
			if not b:
				r = b'{"e":1, "msg": "Blob does not exist."}\n'
				start_response("404 NOT FOUND", [
					("Content-Type", "application/json; charset=utf-8"),
					("Content-Length", len(r)),
				])
				return r,
			
			start_response("200 OK", [
				("Content-Type", b.mime),
				("Content-Length", b.size),
			])
			return wrap_file(env, b.open())
		finally:
			sess.close()
	return wsgi
