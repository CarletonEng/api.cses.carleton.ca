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

import re

from api import app, db

class Course(db.Base):
	""" A course.
	"""
	
	__tablename__ = "tbt-book-course"
	
	__id = db.Column("id", db.Integer, primary_key=True)
	__code = db.Column("code", db.String(8), index=True, nullable=False)
	__bookid = db.Column("bookid", db.ForeignKey("tbt-books.id"))
	
	CODE_STRIP = re.compile("[^A-Z0-9]+")
	CODE_VALID = re.compile("[A-Z]{4}[0-9]{4}")
	
	def __init__(self, code, **kwargs):
		super().__init__(code=code, *kwargs)
	
	@staticmethod
	def code_normalize(code):
		code = code.upper()
		code = Course.CODE_STRIP.sub("", code) # Arguments are backwards.
		
		if not Course.CODE_VALID.fullmatch(code):
			return None
		
		return code
	
	@db.hybrid_property
	def code(self):
		return self.__code
	
	@code.setter
	def code(self, code):
		ncode = Course.code_normalize(code)
		if not ncode:
			raise TypeError("Invalid code "+repr(code))
		self.__code = ncode

class TBTBook(db.Base):
	""" A book.
	"""
	
	__tablename__ = "tbt-books"
	
	id         = db.Column(db.Hex, primary_key=True)
	title      = db.Column(db.String, nullable=False)
	__sellerid = db.Column("sellerid", db.Hex, db.ForeignKey("person.id"))
	
	courses = db.relationship("Course", cascade="all, delete-orphan",
	                          backref=db.backref("book"))
	
	def __init__(self, seller, title, courses=()):
		super().__init__(title=title, seller=seller)
		
		self.courses = [c if isinstance(c, Course) else Course(c) for c in courses]
	
	def __repr__(self):
		return "Blob({})".format(self.id)
