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

from urllib.parse import parse_qs

import api
from api import db
from api.auth import auth, authrequired
from api.person import Person
from api.tbtbook import TBTBook, Course

@api.app.route("/tbt/book")
class index(api.Handler):
	@api.dbs
	@auth
	@api.json_out
	def GET(self):
		uq = parse_qs(self.req.query_string.decode(), keep_blank_values=True)
		
		q = self.dbs.query(TBTBook)
		
		if "sold" not in uq:
			q = q.filter(TBTBook.buyer == None)
		
		if "course" in uq:
			q = q.join(Course).filter(Course.code == uq["course"][0])
		
		if "title" in uq:
			words = uq["title"][0].split(" ")
			
			if len(words) > 10: # You are asking for a lot.
				words = words[:5]
			
			q = q.filter(*(TBTBook.title.ilike("%"+t+"%") for t in words))
		
		return {"e":0,
			"books": [{
				"id": b.id,
				"title": b.title,
				"price": b.price/100,
				"courses": [c.code for c in b.courses],
				"seller": {
					"id": b.seller.id,
					"name": b.seller.name,
				},
				"buyer": b.buyer and b.buyer.id
			} for b in q],
		}
	
	@api.dbs
	@auth
	@api.json_io
	def PUT(self):
		if "tbt" not in self.req.auth.perms:
			self.status_code = 403
			return {"e":1, "msg": "Permission denied."}
		
		if not "title" in self.req.json:
			self.status_code = 400
			return {"e":1, "msg": "Missing Title."}
		if not "price" in self.req.json:
			self.status_code = 400
			return {"e":1, "msg": "Missing Price."}
		if not "courses" in self.req.json:
			self.status_code = 400
			return {"e":1, "msg": "Missing Courses."}
		if not "seller" in self.req.json:
			self.status_code = 400
			return {"e":1, "msg": "Missing Seller."}
		
		seller = self.dbs.query(Person).get(self.req.json["seller"])
		if not seller:
			self.status_code = 400
			return {"e":1, "msg": "Seller does not exist."}
		
		courses = [Course(c) for c in self.req.json["courses"]]
		
		b = TBTBook(seller,
		            self.req.json["title"],
		            int(float(self.req.json["price"])*100),
		            courses)
		self.dbs.add(b)
		self.dbs.commit()
		
		return {"e":0,
			"id": b.id,
		}

@api.app.route("/tbt/book/stats")
class stats(api.Handler):
	@authrequired
	@api.json_out
	def GET(self):
		
		
		return {"e":0,
		}

@api.app.route("/tbt/book/(.*)")
class book(api.Handler):
	@api.dbfetch(TBTBook)
	@auth
	@api.json_out
	def GET(self, b):
		if not self.app.config.debug:
			# Cache for a day unless the dev server.
			# ...or 3 on error.
			self.headers["Cache-Control"] = "max-age=86400,stale-if-error=259200"
		
		return {"e":0,
			"id":  b.id,
			"title": b.title,
			"price": b.price/100,
			"courses": [c.code for c in b.courses],
			"seller": b.seller.id,
			"buyer": b.buyer and b.buyer.id,
		}
	
	@api.dbfetch(TBTBook)
	@authrequired
	@api.json_io
	def PUT(self, b):
		if not "tbt" in self.req.auth.perms:
			self.status_code = 403
			return {"e":0, "msg": "You are not allowed."}
		
		j = self.req.json
		
		if "buyer" in j:
			if b.buyer:
				self.status_code = 409
				return {"e":1, "msg": "Already sold."}
			
			buyer = self.dbs.query(Person).get(j["buyer"])
			if not buyer:
				self.status_code = 400
				return {"e":1, "msg": "Buyer does not exist."}
			
			b.buyer = buyer
		
		self.dbs.commit()
		return {"e":0}
