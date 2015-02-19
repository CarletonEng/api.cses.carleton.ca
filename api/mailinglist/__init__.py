#! /usr/bin/env python3

# Copyright 2015 Kevin Cox

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
###############################################################################

from datetime import datetime

from api import db

class MailingListSub(db.Base):
	""" A Mailing list subscription request.
		
		Instance Attributes:
			id:
				The id of the request.
			date:
				The date the request was received.
			email:
				The email.
	"""
	
	__tablename__ = "mailinglist_sub"
	__table_args__ = {
		"sqlite_autoincrement": True,
	}
	
	id    = db.Column(db.Integer, primary_key=True)
	date  = db.Column(db.DateTime, default=lambda: datetime.utcnow())
	email = db.Column(db.String, unique=True)
