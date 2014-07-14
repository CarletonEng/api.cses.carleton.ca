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
from api.auth import auth
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
			q = q.filter(TBTBook.sold == False)
		
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
				"courses": [c.code for c in b.courses],
				"seller": {
					"id": b.seller.id,
					"name": b.seller.name,
				},
			} for b in q],
		}

@api.app.route("/tbt/book/(.*)")
class person(api.Handler):
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
			"courses": [c.code for c in b.courses],
			"seller": b.seller.id
		}
