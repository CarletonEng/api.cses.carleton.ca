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
from api.banner import Banner, BannerImage

readonly_disable = api.readonly_disable

@api.app.route("/banner(/.*)")
class index(api.Handler):
	@api.dbs
	@api.json_out
	# Seeing a slightly old banner is no big deal but we want it to load fast.
	@api.cache(60*5, 3600*24, 3600*24*14)
	def GET(self, path):
		banners = (self.dbs.query(Banner)
		                   .filter(Banner.path == path)
		                   .filter(Banner.up)
		                   .order_by(Banner.added))
		return {"e":0,
			"banners": [
				{
					"href": b.href,
					"alt": b.alt,
					"images": [{
							"blob": i.blob,
							"w": i.width, "h": i.height,
						} for i in b.images
					]
				} for b in banners
			]
		}
