from datetime import datetime

from api import db

class MailingListSub(db.Base):
	""" A Mailing list subscription request.
		
		Instance Attributes:
			id:
				The id of the request.
			date:
				The date the request was received.
			email:
				The email.
	"""
	
	__tablename__ = "mailinglist_sub"
	__table_args__ = {
		"sqlite_autoincrement": True,
	}
	
	id    = db.Column(db.Integer, primary_key=True)
	date  = db.Column(db.DateTime, default=lambda: datetime.utcnow())
	email = db.Column(db.String, unique=True)
