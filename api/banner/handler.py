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
