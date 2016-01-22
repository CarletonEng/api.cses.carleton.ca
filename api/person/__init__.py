from crypt import crypt
from hmac import compare_digest

import api
from api import db

class Email(db.Base):
	""" Email address.
	"""
	
	__tablename__ = "person_email"
	__table_args__ = (
		db.CheckConstraint("email like '_%@_%'", name="emailvalid"),
	)
	
	email    = db.Column(db.StringStripped, primary_key=True)
	__userid = db.Column("userid", db.ForeignKey("person.id"), nullable=False)
	rank     = db.Column(db.Integer, nullable=False, default=lambda:1)
	
	def __repr__(self):
		return api.autorepr(self, self.email, self.user, self.rank)

class Person(db.Base):
	""" A person.
		
		Instance Attributes:
			id:
				A string containing a unique hex ID representing the user.
			name:
				A string containing the users name.
			auths:
				A list of Auth objects that apply to the user.
			perms:
				A list of strings representing the permissions the user has.
	"""
	
	__tablename__ = 'person'
	
	id       = db.Column(db.Integer, primary_key=True)
	number   = db.Column(db.Integer, unique=True)
	name     = db.Column(db.StringStripped, nullable=False)
	namefull = db.Column(db.StringStripped, nullable=False)
	__pw     = db.Column("pw", db.String, server_default="!", nullable=False)
	perms    = db.Column(db.ListSorted, default=lambda:["selfr", "selfw"])
	
	emails = db.relationship(Email, cascade="all, delete-orphan",
	                         backref=db.backref("user", lazy="joined"))
	
	auths = db.relationship("Auth", foreign_keys="Auth._userid",
	                        cascade="all, delete-orphan",
	                        backref=db.backref("user"))
	
	tbt_books = db.relationship("TBTBook", foreign_keys="TBTBook._sellerid",
	                            backref=db.backref("seller"))
	tbt_booksbought = db.relationship("TBTBook", foreign_keys="TBTBook._buyerid",
	                                  backref=db.backref("buyer"))
	tbt_changes = db.relationship("TBTBookChange", backref=db.backref("user"))
	
	def password_set(self, pw):
		""" Set the password """
		self.__pw = crypt(pw)
	
	def password_check(self, pw):
		""" Check if password is correct """
		return compare_digest(crypt(pw, self.__pw), self.__pw)
	
	def __repr__(self):
		return api.autorepr(self, self.id, self.name, self.perms)
