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
from api.post import Post

@api.app.route("/post")
class index(api.Handler):
	@api.dbs
	@auth
	@api.json_out
	@api.cachehour
	def GET(self):
		uq = parse_qs(self.req.query_string.decode(), keep_blank_values=True)
		
		dbq = self.dbs.query(Post.id, Post.title)
		
		if "dir" in uq:
			dbq = dbq.filter(Post.directory == uq["dir"][-1].rstrip("/"))
		
		return {"e":0,
			"posts": [{"id":id, "title": title} for id, title in dbq],
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
