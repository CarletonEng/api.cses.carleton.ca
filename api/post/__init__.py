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

import api
from api import db

class Post(db.Base):
	""" A post.
		
		Instance Attributes:
			id:
				A string containing a unique hex ID representing the post.
			type:
				The type of document this is.  Can be one of the following:
				- "article": This is a timed "blog-like" post.
				- "page": This is a page.
			content:
				The HTML content of the page.
			perms:
				If false this post is public.  Otherwise a list of permissions
				that can view this post.
	"""
	
	__tablename__ = 'post'
	
	__id    = db.Column("id", db.String, primary_key=True)
	__dir   = db.Column("dir", db.String, index=True)
	type    = db.Column(db.String, default=lambda:"page")
	title   = db.Column(db.String)
	content = db.Column(db.JSON, default=lambda:[]);
	perms   = db.Column(db.JSON, default=None)
	
	@db.hybrid_property
	def id(self):
		return self.__id
	
	@id.setter
	def id(self, v):
		self.__id  = v
		self.__dir, _, _ = v.rpartition("/")
	
	@db.hybrid_property
	def directory(self):
		return self.__dir
	
	def __repr__(self):
		return api.autorepr(self, self.id, self.type)
