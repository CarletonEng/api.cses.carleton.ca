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
from api.post import Post

@api.app.route("/post")
class index(api.Handler):
	@api.dbs
	@auth
	@api.json_out
	@api.cachehour
	def GET(self):
		uq = parse_qs(self.req.query_string.decode(), keep_blank_values=True)
		
		q = self.dbs.query(Post.id)
		
		t = uq.get("type", ("article",))[-1]
		if t != "all":
			q = q.filter(Post.type == t)
		
		if "dir" in uq:
			q = q.filter(Post.directory == uq["dir"][-1].rstrip("/"))
		
		if "prefix" in uq:
			q = q.filter(db.prefixof(Post.id, uq["prefix"][-1]))
		
		orderby = uq.get("order", ("id",))[-1]
		if orderby == "id":
			q = q.order_by(Post.id)
		elif orderby == "title":
			q = q.order_by(Post.title)
		else:
			self.status_code = 400
			return {"e":0, "msg":"Invalid 'order' value."}
		
		return {"e":0,
			"posts": list(q),
		}

@api.app.route("/post/(.*)")
class person(api.Handler):
	@api.dbfetch(Post, 1)
	@auth
	@api.json_out
	@api.cacheday
	def GET(self, p):
		return {"e":0,
			"id":      p.id,
			"type":    p.type,
			"title":   p.title,
			"content": p.content,
		}
	
	@authrequired
	@api.json_io
	def PUT(self, path):
		if not "postw" in self.req.auth.perms:
			return {"e":1,"msg":"You can't edit posts."}
		
		new = False
		p = self.dbs.query(Post).get(path)
		if not p:
			new = True
			p = Post(id=path)
			self.dbs.add(p)
		
		j = self.req.json
		
		if "type" in j:
			p.type = j["type"]
		if "title" in j:
			p.title = j["title"]
		if "content" in j:
			p.content = j["content"]
		
		self.dbs.commit()
		return {"e":0,
			"new": new,
		}
