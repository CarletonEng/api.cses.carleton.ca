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
from api.auth import Auth, auth

def fetchuser(f):
	""" Converts first argument to Person from id."""
	@api.dbs
	def w(self, id):
		try:
			int(id, 16)
		except:
			self.status_code = 400
			self.data = '{"e":400, "msg": "id must be a hex string."}\n'
			return
		
		p = self.dbs.query(Person).filter(Person.id == id).first()
		if not p:
			self.status_code = 404
			self.data = '{"e":404, "msg": "Person does not exist."}\n'
			return
		
		return f(self, p)
	return w

@api.app.route("/person")
class index(api.Handler):
	@api.json_io
	@api.dbs
	def PUT(self):
		j = self.req.json
		
		p = Person()
		self.dbs.add(p)
		
		if "name" in j:
			p.name = j["name"]
		
		self.dbs.commit()
		
		return {"e": 0,
			"id": p.id,
		}

@api.app.route("/person/([^/]*)")
class person(api.Handler):
	@fetchuser
	@api.json_out
	def GET(self, p):
		return {"e":0,
			"id":       p.id,
			"name":     p.name,
			"namefull": p.namefull,
			"perms":    p.perms,
		}
	
	@fetchuser
	@auth
	@api.json_io
	def PUT(self, p):
		j = self.req.json
		
		if "name" in j:
			p.name = j["name"]
		if "namefull" in j:
			p.namefull = j["namefull"]
		
		self.dbs.commit()
		return {"e":0}