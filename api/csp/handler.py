import api
from api import db
from api.csp import CSPViolation, CSPReport

@api.app.route("/csp")
class index(api.Handler):
	@api.dbs
	@api.json_in
	def POST(self):
		j = self.req.json
		if not j:
			return
		j = j.get("csp-report")
		if not j:
			return
		
		r = self.dbs.query(CSPReport).filter_by(data=j).scalar()
		if not r:
			r = CSPReport(j)
			self.dbs.add(r)
		
		self.dbs.add(CSPViolation(r,
		                          self.req.headers.get("User-Agent", "not provided"),
		                          self.req.remote_addr))
		
		self.dbs.commit()
		
		self.content_type = "text/pain; charset=utf-8"
		self.data = "OK"
