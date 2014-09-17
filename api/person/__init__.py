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

from crypt import crypt
from hmac import compare_digest

import api
from api import db

class Email(db.Base):
	""" Email address.
	"""
	
	__tablename__ = "person_email"
	
	email    = db.Column(db.StringStripped, primary_key=True)
	__userid = db.Column("userid", db.ForeignKey("person.id"), primary_key=True)
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
	number   = db.Column(db.Integer, unique=True, nullable=False)
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
