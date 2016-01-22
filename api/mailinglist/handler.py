import api
from api import auth

@api.app.route("/mailinglist")
class index(api.Handler):
	@auth.authrequired
	@api.json_out
	def GET(self):
		if not "mailinglist" in self.req.auth.perms:
			self.status_code = 403
			return {"e": 1, "msg": "You don't have permission."}
		
		q = self.dbs.query(
			MailingListSub.id,
			MailingListSub.date,
			MailingListSub.email
		)
		
		r = list(q)
		maxid = 0
		for i, v in enumerate(r):
			maxid = max(maxid, v[0])
			r[i] = {
				"date":  v[1].timestamp(),
				"email": v[2],
			}
		
		return {"e": 0,
			"requests": r,
			"deletionkey": maxid,
		}
	
	@api.dbs
	@api.json_io
	def POST(self):
		j = self.req.json
		if not j:
			return
		
		if not "email" in j:
			self.status_code = 400
			return {"e": 1, "msg": "Email required."}
		
		self.dbs.add(MailingListSub(
			email = j["email"]
		))
		
		try: self.dbs.commit()
		except db.IntegrityError as e:
			if not "UNIQUE" in repr(e):
				raise
			
			return {"e": 0, "pending": True}
		
		return {"e":0}
	
	@auth.authrequired
	@api.json_io
	def DELETE(self):
		if not "mailinglist" in self.req.auth.perms:
			self.status_code = 403
			return {"e": 1, "msg": "You don't have permission."}
		
		j = self.req.json
		
		if not "key" in j:
			self.status_code = 400
			return {"e":1, "msg": "Deletion key required."}
		key = j["key"]
		
		q = self.dbs.query(MailingListSub).filter(MailingListSub.id <= key)
		q.delete(synchronize_session=False)
		
		self.dbs.commit()
		
		return {"e":0}
