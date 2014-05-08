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
from api.auth import auth
from api.post import Post

def fetchpost(f):
	""" Converts first argument to Post from id."""
	@api.dbs
	def w(self, id):
		p = self.dbs.query(Post).get(id)
		if not p:
			self.status_code = 404
			self.data = '{"e":1, "msg": "Post does not exist."}\n'
			return
		
		return f(self, p)
	return w

@api.app.route("/post")
class index(api.Handler):
	pass

@api.app.route("/post/([^/]*)")
class person(api.Handler):
	@fetchpost
	@auth
	@api.json_out
	def GET(self, p):
		if "localhost" not in self.req.host:
			# Cache for a day unless the dev server.
			# ...or 3 on error.
			self.headers["Cache-Control"] = "max-age=86400,stale-if-error=259200"
		
		return {"e":0,
			"id":      p.id,
			"type":    p.type,
			"title":   p.title,
			"content": p.content,
		}
