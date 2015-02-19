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
from api.auth import authrequired
from api.mailinglist import MailingListSub

@api.app.route("/mailinglist")
class index(api.Handler):
	@authrequired
	@api.json_out
	def GET(self):
		if not "mailinglist" in self.req.auth.perms:
			self.status_code = 403
			return {"e": 1, "msg": "You don't have permission."}
		
		q = self.dbs.query(
			MailingListSub.id,
			MailingListSub.date,
			MailingListSub.email
		)
		
		r = list(q)
		maxid = 0
		for i, v in enumerate(r):
			maxid = max(maxid, v[0])
			r[i] = {
				"date":  v[1].timestamp(),
				"email": v[2],
			}
		
		return {"e": 0,
			"requests": r,
			"deletionkey": maxid,
		}
	
	@api.dbs
	@api.json_io
	def POST(self):
		j = self.req.json
		if not j:
			return
		
		if not "email" in j:
			self.status_code = 400
			return {"e": 1, "msg": "Email required."}
		
		self.dbs.add(MailingListSub(
			email = j["email"]
		))
		
		try: self.dbs.commit()
		except db.IntegrityError as e:
			if not "UNIQUE" in repr(e):
				raise
			
			return {"e": 0, "pending": True}
		
		return {"e":0}
	
	@authrequired
	@api.json_io
	def DELETE(self):
		if not "mailinglist" in self.req.auth.perms:
			self.status_code = 403
			return {"e": 1, "msg": "You don't have permission."}
		
		j = self.req.json
		
		if not "key" in j:
			self.status_code = 400
			return {"e":1, "msg": "Deletion key required."}
		key = j["key"]
		
		q = self.dbs.query(MailingListSub).filter(MailingListSub.id <= key)
		q.delete(synchronize_session=False)
		
		self.dbs.commit()
		
		return {"e":0}
