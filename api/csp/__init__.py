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
###############################################################################

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
	__reportid = db.Column("reportid", db.ForeignKey("csp-report.id"))
	
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
	__tablename__ = "csp-report"
	
	id    = db.Column(db.Hex, primary_key=True)
	data  = db.Column(db.JSON(sort=True), index=True, unique=True);
	violations = db.relationship("CSPViolation", cascade="all, delete-orphan",
	                             backref=db.backref("report"))
	
	def __init__(self, data):
		self.data = data
