from datetime import datetime

from api import db

class CSPViolation(db.Base):
	""" A CSP violation.
		
		This records a message received from a browser about a CSP violation.
		
		Instance Attributes:
			id:
				A string containing a unique hex ID representing the violation.
			date:
				The date the report was received.
			source:
				The source ip.
			useragent:
				The user agent.
			report:
				The report data.
	"""
	
	__tablename__ = "csp"
	
	id         = db.Column(db.Hex, primary_key=True)
	date       = db.Column(db.DateTime, default=lambda: datetime.utcnow())
	source     = db.Column(db.String)
	useragent  = db.Column(db.String)
	__reportid = db.Column("reportid", db.ForeignKey("csp_report.id"))
	
	def __init__(self, report, ua="not provided", ip="not provided"):
		self.report = report
		self.useragent = ua
		self.source = ip

class CSPReport(db.Base):
	""" The report data.
		
		The json object received from the browser.
		
		Instance Attributes:
			data:
				The object from the browser.
			violations:
				The reports that sent this object.
	"""
	__tablename__ = "csp_report"
	
	id    = db.Column(db.Hex, primary_key=True)
	data  = db.Column(db.JSON(sort=True), index=True, unique=True);
	violations = db.relationship("CSPViolation", cascade="all, delete-orphan",
	                             backref=db.backref("report"))
	
	def __init__(self, data):
		self.data = data
