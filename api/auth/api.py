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
import api.db as db

from api.person import Person
from api.auth import Auth

@api.app.route("/auth")
class index(api.Handler):
	@api.json_io
	@api.dbs
	def POST(self):
		j = self.req.json
		s = self.dbs
		
		if not "user" in j:
			self.status_code = 400
			return {"e":400, "msg":"No user provided."}
		if not "pass" in j:
			self.status_code = 400
			return {"e":400, "msg":"No password provided."}
		
		p = s.query(Person).filter(Person.id == j["user"]).first()
		if not p or not p.password_check(j["pass"]):
			self.status_code = 403
			return {"e":403, "msg":"Invalid credentials."}
		
		a = Auth(p)
		s.add(a)
		s.commit()
		
		return {
			"e": 0,
			"token": a.token,
		}
