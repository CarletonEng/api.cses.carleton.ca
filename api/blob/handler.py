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
from api.auth import auth, authrequired
from api.blob import Blob

readonly_disable = api.readonly_disable

@api.app.route("/blob")
class index(api.Handler):
	@readonly_disable
	@api.dbs
	@authrequired
	@api.json_out
	def PUT(self):
		if not "upload" in self.req.auth.perms:
			# The client doesn't actually get this for larger files because the
			# connection gets aborted when we don't accept their upload.
			
			self.status_code = 403
			return {"e":1, "msg": "You can't upload."}
		
		b = Blob(mime=self.req.mimetype)
		b.writestream(self.req.stream)
		
		new = True
		sb = self.dbs.query(Blob).get(b.id)
		if sb: # We already have this blob.
			b = sb
			new = False
		else: # Save the new one.
			self.dbs.add(b)
			self.dbs.commit()
		
		self.status_code = 201 if new else 200
		self.headers["Location"] = "/blob/"+b.id
		
		return {"e": 0,
			"id": b.id,
			"new": new,
		}

@api.app.route("/blob/([A-Fa-f0-9]*)(?:/.*)?")
def blob(app, req, id):
	id = id.upper()
	
	def wsgi(env, start_response):
		# Handle ETags.
		if env.get("HTTP_IF_NONE_MATCH", "") == '"'+id+'"':
			start_response("304 NOT MODIFIED", [
				("Cache-Control", "no-cache" if app.config.debug else "public,max-age=31536000")
				("Access-Control-Allow-Origin", env.get("HTTP_ORIGIN", "")),
				("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE"),
				("Access-Control-Allow-Headers", "Accept, Authorization, Content-Type, X-CSES-Path"),
				("Access-Control-Max-Age", "31536000"),
			])
			return ()
		
		sess = db.Session()
		try:
			b = sess.query(Blob).get(id)
			if not b:
				r = b'{"e":1,"msg":"Blob does not exist."}\n'
				start_response("404 NOT FOUND", [
					("Content-Type", "application/json; charset=utf-8"),
					("Content-Length", str(len(r))),
					("Access-Control-Allow-Origin", env.get("HTTP_ORIGIN", "")),
					("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE"),
					("Access-Control-Allow-Headers", "Accept, Authorization, Content-Type, X-CSES-Path"),
					("Access-Control-Max-Age", "31536000"),
				])
				return r,
			
			h = [
				("Content-Type", b.mime),
				("Content-Length", str(b.size)),
				("ETag", '"'+b.id+'"'),
				("Cache-Control", "no-cache" if app.config.debug else "public,max-age=31536000")
				("Access-Control-Allow-Origin", env.get("HTTP_ORIGIN", "")),
				("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE"),
				("Access-Control-Allow-Headers", "Accept, Authorization, Content-Type, X-CSES-Path"),
				("Access-Control-Max-Age", "31536000"),
			]
			if b.enc:
				h.append(("Content-Encoding", b.enc))
			
			start_response("200 OK", h)
			return wrap_file(env, b.open())
		finally:
			sess.close()
	return wsgi
