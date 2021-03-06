from datetime import datetime
import re

import api
from api import app, db

class CourseCode(db.TypeDecorator):
	""" A Course code
		It does some normalization and validation.
	"""
	impl = db.String
	
	CODE_STRIP = re.compile("[^A-Z0-9]+")
	CODE_VALID = re.compile("[A-Z]{4}[0-9]{4}$")
	
	def __init__(self):
		super().__init__(8)
	
	@staticmethod
	def clean(code):
		return CourseCode.CODE_STRIP.sub("", code.upper())
	
	@staticmethod
	def raw_valid(code):
		return CourseCode.CODE_VALID.match(code)
	
	@staticmethod
	def valid(code):
		return CourseCode.raw_valid(CourseCode.clean(code))
	
	def process_bind_param(self, value, dialect):
		code = CourseCode.clean(value)
		
		if not CourseCode.raw_valid(code):
			return None
		
		return code
	
	def coerce_compared_value(self, op, val):
		return db.String()

class Course(db.Base):
	""" A course.
	"""
	
	__tablename__ = "tbt_book_course"
	
	__id    = db.Column("id", db.Integer, primary_key=True)
	code    = db.Column("code", CourseCode, nullable=False)
	_bookid = db.Column("bookid", db.ForeignKey("tbt_book.id"))
	
	def __init__(self, code, **kwargs):
		super().__init__(code=code, *kwargs)
	
	def __repr__(self):
		return repr(self.code)

# Include the other parameter for a covering index.
db.Index("tbt_book_course_code_idx",    Course.code,    Course._bookid)
db.Index("tbt_book_course_code_revidx", Course._bookid, Course.code)

class TBTBookChange(db.Base):
	__tablename__ = "tbt_book_change"
	
	__id = db.Column("id", db.Hex, primary_key=True)
	time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow())
	__userid = db.Column("user", db.ForeignKey("person.id"))
	__bookid = db.Column("book", db.ForeignKey("tbt_book.id"))
	
	desc = db.Column(db.StringStripped, nullable=False)

class TBTBook(db.Base):
	""" A book.
	"""
	
	__tablename__ = "tbt_book"
	
	id        = db.Column(db.Integer, primary_key=True)
	title     = db.Column(db.StringStripped, nullable=False)
	author    = db.Column(db.StringStripped, nullable=False)
	edition   = db.Column(db.StringStripped, default="", server_default="")
	price     = db.Column(db.Integer, nullable=False)
	paid      = db.Column(db.Boolean(name="paid_bool"),
	                                 default=False,
	                                 server_default=db.expression.false())
	_sellerid = db.Column("seller", db.ForeignKey("person.id"), index=True, nullable=False)
	_buyerid  = db.Column("buyer", db.ForeignKey("person.id"), index=True)
	
	courses = db.relationship("Course", cascade="all, delete-orphan",
	                          backref=db.backref("book"), lazy="joined")
	
	changes = db.relationship("TBTBookChange", cascade="all, delete-orphan",
	                          backref=db.backref("book"))
	
	def __init__(self, *, courses=[], **kwargs):
		super().__init__(**kwargs)
		
		self.courses = [c if isinstance(c, Course) else Course(c) for c in courses]
	
	def __repr__(self):
		return api.autorepr(self, self.id,
		                    title=self.title,
		                    edition=self.edition,
		                    author=self.author,
		                    price=self.price,
		                    buyer=self.buyer,
		                    seller=self.seller)
