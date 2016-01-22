from urllib.parse import parse_qs

import api
from api import db
from api.person import Person, Email
from api.auth import Auth, auth, authrequired

readonly_disable = api.readonly_disable

class HandlerPerson(api.Handler):
	def canwrite(self, p):
		if not self.req.auth:
			return False
		
		if "personw" in self.req.auth.perms:
			return True
		if self.req.auth.user == p and "selfw" in self.req.auth.perms:
			return True
		
		return False

@api.app.route("/person")
class index(HandlerPerson):
	SEARCH_RESULTS_MAX     = 1024
	SEARCH_RESULTS_DEFAULT =   32
	
	@auth
	@api.json_out
	@api.dbs
	@api.cachemin
	def GET(self):
		uq = parse_qs(self.req.query_string.decode(), keep_blank_values=True)
		
		q = self.dbs.query(Person)
		
		all = self.req.auth and "personr" in self.req.auth.perms
		
		if "name" in uq:
			n = "%"+uq["name"][0]+"%"
			q = q.filter(Person.name.ilike(n) | Person.namefull.ilike(n))
		
		if "number" in uq:
			if not all:
				self.status_code = 403
				return {"e":0, "msg":"You may not filter by student number."}
			
			s = uq["number"][0]
			mult = 10**(9-len(s))
			n = int(s)
			minn = (n  ) * mult
			maxn = (n+1) * mult
			
			q = q.filter(Person.number >= minn, Person.number < maxn)
		
		limit = index.SEARCH_RESULTS_DEFAULT
		if "limit" in uq:
			limit = int(uq["limit"][0])
		limit = min(limit, index.SEARCH_RESULTS_MAX)
		
		q = q.limit(limit)
		
		return {"e":0,
			"people": [{
				"id":       p.id,
				"name":     p.name,
				"namefull": p.namefull,
				"number":   p.number if all else None,
			} for p in q]
		}
	
	@readonly_disable
	@api.cachenostore
	@authrequired
	@api.json_io
	@api.dbs
	def PUT(self):
		j = self.req.json
		
		if "personw" not in self.req.auth.perms:
			self.status_code = 403
			return {"e":1, "msg":"You don't have permission to do that."}
		
		p = Person()
		self.dbs.add(p)
		
		if not ("name" in j and j["name"]):
			self.status_code = 400
			return {"e":1, "msg":"Name required."}
		if not ("namefull" in j and j["namefull"]):
			self.status_code = 400
			return {"e":1, "msg":"Full name required."}
		if not ("emails" in j and j["emails"]):
			self.status_code = 400
			return {"e":1, "msg":"At least one email is required."}
		
		p.name     = j["name"]
		p.namefull = j["namefull"]
		
		if "number" in j:
			p.number = j["number"]
		
		
		if "emails" in j:
			p.emails = [Email(email=e) for e in j["emails"]]
		
		self.dbs.commit()
		
		return {"e":0,
			"id": p.id,
		}

@api.app.route("/person/(\\d*)")
class person(HandlerPerson):
	@api.dbfetchint(Person)
	@auth
	@api.json_out
	@api.cachehour
	def GET(self, p):
		all = self.canwrite(p)
		
		r = {"e":0,
			"id":       p.id,
			"name":     p.name,
			"namefull": p.namefull,
		}
		if all:
			r.update({
				"perms": p.perms,
				"number": p.number,
				"emails": [{
					"email": e.email,
					"rank": e.rank,
				} for e in p.emails]
			})
		
		return r
	
	@readonly_disable
	@api.cachenostore
	@api.dbfetchint(Person)
	@auth
	@api.json_io
	def PUT(self, p):
		j = self.req.json
		
		if not self.canwrite(p):
			self.status_code = 403
			return {"e":1, "msg":"You can't modify this person."}
		
		if "name" in j:
			p.name = j["name"]
		if "namefull" in j:
			p.namefull = j["namefull"]
		if "perms" in j and j["perms"] != p.perms:
			if "wheel" not in self.req.auth.perms:
				self.status_code = 403
				return {"e":1,"msg": "You aren't allowed to do that."}
			
			p.perms = j["perms"]
			
			# Delete existing sessions.
			# self.dbs.query(Auth).filter(Auth.user == p).delete()
			for a in p.auths:
				self.dbs.delete(a)
		
		self.dbs.commit()
		return {"e":0, "id":p.id}

@api.app.route("/person/(\\d*)/pass")
class person(HandlerPerson):
	@readonly_disable
	@api.dbfetch(Person)
	@authrequired
	@api.json_io
	def PUT(self, p):
		j = self.req.json
		
		if not self.canwrite(p):
			self.status_code = 403
			return {"e":1, "msg":"You can't modify this person."}
		
		if "wheel" in p.perms and "wheel" not in self.req.auth.perms:
			self.status_code = 403
			return {"e":1, "msg":"Only an admin can modify this user's password."}
		
		if not "pass" in j:
			self.status_code = 400
			return {"e":1, "msg":"You must provide a new password."}
		
		p.password_set(j["pass"])
		
		# Delete existing sessions (except this one).
		for a in p.auths:
			if a != self.req.auth:
				self.dbs.delete(a)
		
		self.dbs.commit()
		
		return {"e":0}
