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

class Post(db.Base):
	""" A post.
		
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
	
	__tablename__ = 'posts'
	
	id       = db.Column(db.Hex, primary_key=True)
	slug     = db.Column(db.String)
	title   = db.Column(db.String)
	content  = db.Column(db.JSON, default=lambda:[]);
	perm    = db.Column(db.JSON, default=None)
	
	def __repr__(self):
		return "Post({}, {})".format(self.id, self.slug)
