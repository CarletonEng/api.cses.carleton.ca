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
################################################################################

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
	CODE_VALID = re.compile("[A-Z]{4}[0-9]{4}")
	
	def __init__(self):
		super().__init__(8)
	
	@staticmethod
	def clean(code):
		return CourseCode.CODE_STRIP.sub("", code.upper())
	
	def process_bind_param(self, value, dialect):
		code = CourseCode.clean(value)
		
		if not CourseCode.CODE_VALID.fullmatch(code):
			return None
		
		return code
	
	def coerce_compared_value(self, op, val):
		return db.String()

class Course(db.Base):
	""" A course.
	"""
	
	__tablename__ = "tbt_book_course"
	
	__id = db.Column("id", db.Integer, primary_key=True)
	code = db.Column("code", CourseCode, index=True, nullable=False)
	__bookid = db.Column("bookid", db.ForeignKey("tbt_book.id"))
	
	def __init__(self, code, **kwargs):
		super().__init__(code=code, *kwargs)

class TBTBookChange(db.Base):
	__tablename__ = "tbt_book_change"
	
	__id = db.Column("id", db.Hex, primary_key=True)
	time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow())
	__userid = db.Column("user", db.ForeignKey("person.id"))
	__bookid = db.Column("book", db.ForeignKey("tbt_book.id"))
	
	desc = db.Column(db.String, nullable=False)

class TBTBook(db.Base):
	""" A book.
	"""
	
	__tablename__ = "tbt_book"
	
	id        = db.Column(db.Hex, primary_key=True)
	title     = db.Column(db.String, nullable=False)
	author    = db.Column(db.String, nullable=False)
	edition   = db.Column(db.String, default="1st")
	price     = db.Column(db.Integer, nullable=False)
	_buyerid  = db.Column("buyer", db.ForeignKey("person.id"))
	_sellerid = db.Column("seller", db.ForeignKey("person.id"))
	
	courses = db.relationship("Course", cascade="all, delete-orphan",
	                          backref=db.backref("book"))
	
	changes = db.relationship("TBTBookChange", cascade="all, delete-orphan",
	                          backref=db.backref("book"))
	
	def __init__(self, seller, title, author, price, courses=(), **kwargs):
		super().__init__(title=title,
		                 author=author,
		                 price=price,
		                 seller=seller,
		                 **kwargs)
		
		self.courses = [c if isinstance(c, Course) else Course(c) for c in courses]
	
	def __repr__(self):
		return api.autorepr(self, self.id,
		                    title=self.title,
		                    edition=self.edition,
		                    author=self.author,
		                    price=self.price,
		                    buyer=self.buyer,
		                    seller=self.seller)
