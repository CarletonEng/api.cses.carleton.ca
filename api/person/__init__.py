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

import api.db as db
from api.perm import Perm

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
				A list of Perm objects that the user has.
	"""
	
	__tablename__ = 'person'
	
	id   = db.Column(db.Hex, primary_key=True)
	name = db.Column(db.String)
	__pw = db.Column(db.String, server_default="!")
	
	auths = db.relationship("Auth", cascade="all, delete-orphan",
	                        backref=db.backref("user", lazy="joined"))
	
	perms = db.relationship("Perm", cascade="all, delete-orphan", lazy="joined",
	                         backref=db.backref("user", lazy="joined"))
	
	def password_set(self, pw):
		""" Set the password """
		self.__pw = crypt(pw)
	
	def password_check(self, pw):
		""" Check if password is correct """
		return compare_digest(crypt(pw, self.__pw), self.__pw)
	
	def perm_has(self, perm):
		""" Check if person has permission `perm` """
		return Perm(perm) in self.perms
	
	def __repr__(self):
		return "Person({}, {}, perms={})".format(self.id,
		                                         repr(self.name),
		                                         repr(self.perms))
