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

import api.db as db

class Perm(db.Base):
	""" A permission.
		
		Permissions are identified by their `name`.
	"""
	__tablename__ = 'perm'
	
	__id     = db.Column(db.Integer, primary_key=True)
	name     = db.Column(db.String)
	__userid = db.Column(db.Hex, db.ForeignKey("person.id"))
	
	def __eq__(self, that):
		if instanceof(that, Perm):
			return this.name == that.name
		else:
			return this.name == that
	
	def __repr__(self):
		return "Perm({}, {})".format(self.name, repr(self.user))
