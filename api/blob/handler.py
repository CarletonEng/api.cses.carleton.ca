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
		cors = [
			("Access-Control-Allow-Origin", env.get("HTTP_ORIGIN", "")),
			("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE"),
			("Access-Control-Allow-Headers", "Accept, Authorization, Content-Type, X-CSES-Path"),
			("Access-Control-Max-Age", "31536000"),
		]
		
		# Handle ETags.
		if env.get("HTTP_IF_NONE_MATCH", "") == '"'+id+'"':
			start_response("304 NOT MODIFIED", [
				("Cache-Control", "no-cache" if app.config.debug else "public,max-age=31536000"),
			] + cors)
			return ()
		
		sess = db.Session()
		try:
			b = sess.query(Blob).get(id)
			if not b:
				r = b'{"e":1,"msg":"Blob does not exist."}\n'
				start_response("404 NOT FOUND", [
					("Content-Type", "application/json; charset=utf-8"),
					("Content-Length", str(len(r))),
				] + cors)
				return r,
			
			h = [
				("Content-Type", b.mime),
				("Content-Length", str(b.size)),
				("ETag", '"'+b.id+'"'),
				("Cache-Control", "no-cache" if app.config.debug else "public,max-age=31536000")
			]
			if b.enc:
				h.append(("Content-Encoding", b.enc))
			
			start_response("200 OK", h+cors)
			return wrap_file(env, b.open())
		finally:
			sess.close()
	return wsgi
