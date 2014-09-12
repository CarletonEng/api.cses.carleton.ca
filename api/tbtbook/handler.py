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
from api.tbtbook import TBTBook, TBTBookChange, Course, CourseCode

@api.app.route("/tbt/book")
class index(api.Handler):
	@api.dbs
	@api.json_out
	@api.cachemin
	def GET(self):
		uq = parse_qs(self.req.query_string.decode(), keep_blank_values=True)
		
		q = self.dbs.query(TBTBook.id)
		
		if "sold" not in uq:
			q = q.filter(TBTBook.buyer == None)
		
		if "course" in uq:
			c = CourseCode.clean(uq["course"][0])
			print (c)
			
			if len(c) == 8:
				p = Course.code == c
			else:
				p = Course.code.like(c+"%")
			
			q = q.join(Course).filter(p)
		
		if "title" in uq:
			words = uq["title"][0].split(" ")
			
			if len(words) > 10: # You are asking for a lot.
				words = words[:5]
			
			q = q.filter(*(TBTBook.title.ilike("%"+t+"%") for t in words))
		
		q = q.group_by(TBTBook.id)
		
		return {"e":0,
			"books": [r[0] for r in q],
		}
	
	@api.cachenostore
	@api.dbs
	@auth
	@api.json_io
	def PUT(self):
		if "tbt" not in self.req.auth.perms:
			self.status_code = 403
			return {"e":1, "msg": "Permission denied."}
		
		if not "authorizer" in self.req.json:
			self.status_code = 400
			return {"e":1, "msg": "The authorizer is required."}
		if not "title" in self.req.json:
			self.status_code = 400
			return {"e":1, "msg": "Missing Title."}
		if not "author" in self.req.json:
			self.status_code = 400
			return {"e":1, "msg": "Missing Author."}
		if not "price" in self.req.json:
			self.status_code = 400
			return {"e":1, "msg": "Missing Price."}
		if not "courses" in self.req.json:
			self.status_code = 400
			return {"e":1, "msg": "Missing Courses."}
		if not "seller" in self.req.json:
			self.status_code = 400
			return {"e":1, "msg": "Missing Seller."}
		
		authorizer = self.dbs.query(Person).get(self.req.json["authorizer"])
		if not authorizer:
			self.status_code = 400
			return {"e":1, "msg": "Authorizer is not a person."}
		if not "tbt" in authorizer.perms:
			self.status_code = 403
			return {"e":1, "msg": "Authorizer is not allowed to make changes."}
		
		seller = self.dbs.query(Person).get(self.req.json["seller"])
		if not seller:
			self.status_code = 400
			return {"e":1, "msg": "Seller does not exist."}
		
		courses = []
		
		for c in self.req.json["courses"]:
			if not CourseCode.valid(c):
				self.status_code = 400
				return {"e":1, "msg":"Invalid course code '"+c+"'."}
			
			courses.append(Course(c))
		
		b = TBTBook(seller=seller,
		            title=self.req.json["title"],
		            author=self.req.json["author"],
		            price=int(float(self.req.json["price"])*100),
		            courses=courses)
		
		if "edition" in self.req.json:
			b.edition = str(self.req.json["edition"])
		
		c = TBTBookChange(book=b,
		                  desc="created\n"+repr(b),
		                  user=authorizer)
		self.dbs.add(b, c)
		self.dbs.commit()
		
		return {"e":0,
			"id": b.id,
		}

@api.app.route("/tbt/book/stats")
class stats(api.Handler):
	@api.cachemin
	@authrequired
	@api.json_out
	def GET(self):
		if not "tbt" in self.req.auth.perms:
			self.status_code = 403
			return {"e":1, "msg":"You are not allowed to see the stats."}
		
		total = self.dbs.query(
			db.func.count(TBTBook.price), db.func.sum(TBTBook.price)
		)
		sold = total.filter(TBTBook.buyer != None)
		paid = total.filter(TBTBook.paid == True)
		
		b,  p  = total.one()
		bs, ps = sold.one()
		bp, pp = sold.one()
		
		# A sum of no elements is None, not 0
		
		p  = p  or 0
		ps = ps or 0
		pp = pp or 0
		
		return {"e":0,
			"books": b,
			"price": p/100,
			"bookssold": bs,
			"pricesold": ps/100,
			"bookspaid": bp,
			"pricepaid": pp/100,
		}

@api.app.route("/tbt/book/([^/]*)")
class book(api.Handler):
	@api.dbfetch(TBTBook)
	@auth
	@api.json_out
	@api.cachemin
	def GET(self, b):
		
		r = {"e":0,
			"title":   b.title,
			"edition": b.edition,
			"author":  b.author,
			"price":   b.price/100,
			"courses": [c.code for c in b.courses],
		}
		
		if self.req.auth and "tbt" in self.req.auth.perms:
			r.update({
				"paid": b.paid,
				"seller":  b.seller.id,
				"buyer":   b.buyer and b.buyer.id,
			})
		
		return r;
	
	@api.dbfetch(TBTBook)
	@authrequired
	@api.json_io
	def PUT(self, b):
		if not "tbt" in self.req.auth.perms:
			self.status_code = 403
			return {"e":1, "msg": "You are not allowed."}
		
		j = self.req.json
		
		if not "authorizer" in j:
			self.status_code = 400
			return {"e":1, "msg":"Authorizer Required"}
		authorizer = self.dbs.query(Person).get(j["authorizer"])
		if not authorizer:
			self.status_code = 400
			return {"e":1, "msg":"Authorizer does not exist."}
		if not "tbt" in authorizer.perms:
			self.status_code = 403
			return {"e":1, "msg":"Authorizer is not allowed to make changes."}
		
		if "buyer" in j:
			if b.buyer:
				self.status_code = 409
				return {"e":1, "msg": "Already sold."}
			
			buyer = self.dbs.query(Person).get(j["buyer"])
			if not buyer:
				self.status_code = 400
				return {"e":1, "msg": "Buyer does not exist."}
			
			b.buyer = buyer
			c = TBTBookChange(book=b,
			                  desc="sold book to \n"+repr(buyer),
			                  user=authorizer)
		
		if "paid" in j:
			if not b.buyer:
				self.status_code = 400
				return {"e":1, "msg":"Can't sell a book without a buyer."}
			if not j["paid"]:
				self.status_code = 400
				return {"e":1, "msg":"Can't unpay a seller."}
			if b.paid:
				self.status_code = 409
				return {"e":1, "msg":"Seller has already been paid."}
			
			b.paid = True
			c = TBTBookChange(book=b,
			                  desc="paid buyer:\n"+repr(b.buyer),
			                  user=authorizer)
		
		self.dbs.commit()
		return {"e":0,
			"id": b.id,
		}
	
	@api.dbfetch(TBTBook)
	@authrequired
	@api.json_out
	def DELETE(self, b):
		if not "tbt" in self.req.auth.perms:
			self.status_code = 403
			return {"e":1, "msg": "You are not allowed."}
		
		print("Deleting", repr(b))
		self.dbs.delete(b)
		self.dbs.commit()
		
		return {"e":0}

@api.app.route("/tbt/book/([^/]*)/changes")
class book(api.Handler):
	@api.dbfetch(TBTBook)
	@authrequired
	@api.json_out
	@api.cachemin
	def GET(self, b):
		if not "tbt" in self.req.auth.perms:
			self.status_code = 403
			return {"e":1, "msg":"You are not allowed to see changes."}
		
		return {"e":0,
			"changes": [ {
					"by":   c.user.id,
					"time": c.time.timestamp(),
					"desc": c.desc,
				} for c in b.changes
			],
		}
