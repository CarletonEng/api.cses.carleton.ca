import api
from api import db

from api.person import Person, Email
from api.auth import Auth

readonly_disable = api.readonly_disable

@api.app.route("/auth")
class index(api.Handler):
	@api.dbs
	@api.cachehour
	@api.auth.authrequired
	@api.json_out
	def GET(self):
		return {"e":0,
			"perms": self.req.auth.perms,
			"user": self.req.auth._userid,
		}
	
	@api.cachenostore
	@api.json_io
	@api.dbs
	def POST(self):
		j = self.req.json
		s = self.dbs
		
		user = j.get("user")
		if not user:
			self.status_code = 400
			return {"e":1, "msg":"No user provided."}
		if not isinstance(user, str):
			self.status_code = 400
			return {"e":1, "msg":"'user' must be a string."}
		
		pw = j.get("pass")
		if not pw:
			self.status_code = 400
			return {"e":1, "msg":"No password provided."}
		
		if "@" in user:
			person = s.query(Person).join(Email).filter_by(email=user).scalar()
		else:
			person = s.query(Person).get(user)
		
		if not person or not person.password_check(j["pass"]):
			self.status_code = 403
			return {"e":1, "msg":"Invalid credentials."}
		
		a = Auth(person)
		s.add(a)
		
		a.perms = person.perms
		
		s.commit()
		
		return {"e":0,
			"token": a.token,
			"perms": a.perms,
			"user": a.user.id,
		}

@api.app.route("/auth/invalidate")
class index(api.Handler):
	@api.cachenostore
	@api.dbs
	@api.auth.authrequired
	@api.json_out
	def POST(self):
		self.dbs.delete(self.req.auth)
		self.dbs.commit()
		
		return {"e":0}
