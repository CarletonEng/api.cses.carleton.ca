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

from api.person import Person
from api.auth import Auth

@api.app.route("/auth")
class index(api.Handler):
	@api.dbs
	@api.auth.authrequired
	@api.json_out
	@api.cacheday
	def GET(self):
		return {"e":0,
			"perms": self.req.auth.perms,
			"user": self.req.auth.user.id,
		}
	
	@api.json_io
	@api.dbs
	def POST(self):
		j = self.req.json
		s = self.dbs
		
		if not "user" in j:
			self.status_code = 400
			return {"e":1, "msg":"No user provided."}
		if not "pass" in j:
			self.status_code = 400
			return {"e":1, "msg":"No password provided."}
		
		p = s.query(Person).get(j["user"])
		if not p or not p.password_check(j["pass"]):
			self.status_code = 403
			return {"e":1, "msg":"Invalid credentials."}
		
		a = Auth(p)
		s.add(a)
		
		a.perms = p.perms
		
		s.commit()
		
		return {"e":0,
			"token": a.token,
			"perms": a.perms,
			"user": a.user.id,
		}

@api.app.route("/auth/invalidate")
class index(api.Handler):
	@api.dbs
	@api.auth.authrequired
	@api.json_out
	def POST(self):
		self.dbs.delete(self.req.auth)
		self.dbs.commit()
		
		return {"e":0}
