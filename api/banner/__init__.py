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

import api
from api import db

class BannerImage(db.Base):
	""" An image for a banner.
	"""
	
	__tablename__ = "banner_image"
	
	id     = db.Column(db.Hex, primary_key=True)
	blob   = db.Column("blob", db.ForeignKey("blob.id"), nullable=False)
	width  = db.Column(db.Integer, nullable=False)
	height = db.Column(db.Integer, nullable=False)
	
	__bannerid = db.Column("banner", db.ForeignKey("banner2.id"), nullable=False)
	
	@classmethod
	def fits(w, h):
		""" Select images that are large enough for the given device.
			
			Creates a filter expression that selects images that are large
			enough to fit the given space (in pixels).
		"""
		return (BannerImage.width >= w) & (BannerImage.height >= h)

class Banner(db.Base):
	""" A banner.
		
		Instance Attributes:
			id:
				A string containing a unique hex ID representing the banner.
			alt:
				Alt text.
	"""
	
	__tablename__ = "banner2"
	
	id      = db.Column(db.Hex, primary_key=True)
	path    = db.Column(db.StringStripped, nullable=False, server_default="/", default="/")
	alt     = db.Column(db.StringStripped)
	href    = db.Column(db.StringStripped)
	added   = db.Column(db.DateTime, default=datetime.utcnow())
	removed = db.Column(db.DateTime)
	
	images = db.relationship("BannerImage", cascade="all, delete-orphan",
	                         lazy="joined", backref=db.backref("banner"))
	
	@db.hybrid_property
	def up(self):
		now = datetime.utcnow()
		return (self.added <= now) & ((now < self.removed) | (self.removed == None))
	
	def __repr__(self):
		return api.autorepr(self, self.id, self.alt)

db.Index("banner2_time", Banner.path, Banner.added, Banner.removed)
