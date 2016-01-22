from urllib.parse import parse_qs

import api
from api import db
from api.auth import auth, authrequired
from api.person import Person
from api.tbtbook import TBTBook, TBTBookChange, Course, CourseCode

def readonly_disable(f):
	if api.app.config.readonly_tbt:
		return api.readonly_responder
	
	return api.readonly_disable(f)

@api.app.route("/tbt/book")
class index(api.Handler):
	@auth
	@api.json_out
	@api.cachemin
	def GET(self):
		uq = parse_qs(self.req.query_string.decode(), keep_blank_values=True)
		
		q = self.dbs.query(TBTBook.id)
		
		if "sold" in uq:
			if uq["sold"][0] == "0":
				q = q.filter(TBTBook.buyer == None)
			else:
				q = q.filter(TBTBook.buyer != None)
		
		if "course" in uq:
			c = CourseCode.clean(uq["course"][0])
			
			if len(c) == 8:
				p = Course.code == c
			else:
				p = db.prefixof(Course.code, c)
			
			q = q.join(Course).filter(p)
		
		if "title" in uq:
			words = uq["title"][0].split(" ")
			
			if len(words) > 10: # You are asking for a lot.
				words = words[:5]
			
			q = q.filter(*(TBTBook.title.ilike("%"+t+"%") for t in words))
		
		if "involves" in uq:
			if not self.req.auth:
				self.status_code = 401
				return {"e":1, "msg":"You must authenticate to filter by involvement."}
			
			inv = int(uq["involves"][0])
			
			if inv != self.req.auth.user.id:
				self.status_code = 403
				return {"e":1, "msg":"You can only search for your own involvement."}
			
			q = q.filter(
				(TBTBook.seller == Person(id=inv)) | (TBTBook.buyer == Person(id=inv))
			)
		
		if "paid" in uq:
			if not self.req.auth:
				self.status_code = 401
				return {"e":1,"msg":"You must authenticate to filter by paid."}
			
			if not "tbt" in self.req.auth.perms:
				self.status_code = 403
				return {"e":1, "msg":"You may not filter by paid."}
			
			paid = uq["paid"][-1]
			
			q = q.filter(TBTBook.paid == (paid != "0"))
		
		q = q.group_by(TBTBook.id)
		
		return {"e":0,
			"books": [r[0] for r in q],
		}
	
	@readonly_disable
	@api.cachenostore
	@api.dbs
	@authrequired
	@api.json_io
	def PUT(self):
		if not self.hasperm("tbt"):
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
			return {
				"e": 1,
				"msg":
					"Authorizer is not allowed to make changes. " +
					"(They don't have the 'tbt' permission.)",
			}
		
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
		bp, pp = paid.one()
		
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
		
		#TODO: Optimize query, pulling in person.
		
		r = {"e":0,
			"title":   b.title,
			"edition": b.edition,
			"author":  b.author,
			"price":   b.price/100,
			"courses": [c.code for c in b.courses],
			"buyer":   bool(b._buyerid), # Anyone can see if a book is sold.
		}
		
		if self.req.auth and "tbt" in self.req.auth.perms:
			r.update({
				"paid": b.paid,
				"seller":  b._sellerid,
				"buyer":   b._buyerid,
			})
		
		return r;
	
	@readonly_disable
	@api.dbfetch(TBTBook)
	@authrequired
	@api.json_io
	def PUT(self, b):
		if not self.hasperm("tbt"):
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
			return {
				"e": 1,
				"msg":
					"Authorizer is not allowed to make changes. " +
					"(They don't have the 'tbt' permission.)",
			}
		
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
	
	@readonly_disable
	@api.dbfetch(TBTBook)
	@authrequired
	@api.json_out
	def DELETE(self, b):
		if not self.hasperm("tbt"):
			self.status_code = 403
			return {"e":1, "msg": "You are not allowed. ('tbt' permission required.)"}
		
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
