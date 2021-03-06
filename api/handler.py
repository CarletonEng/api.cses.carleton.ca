import api

class Default(api.Handler):
	@api.json_out
	@api.cachehour
	def default(self):
		self.status_code = 404
		return {"e": 404,
			"msg": "The requested URL {} is not part of the API.".format(self.req.path),
		}
api.app.catchall = Default

@api.app.route("/")
class index(api.Handler):
	@api.cacheforever
	def GET(self):
		self.content_type = "text/plain; charset=utf-8"
		self.data = "This is the API, go away.\n"

@api.app.route("/ping")
class ping(api.Handler):
	@api.cachenocache
	def GET(self):
		self.content_type = "application/json; charset=utf-8"
		self.data = '{"e":0,"msg":"pong",uuid":"24c95108-0e85-4260-8083-2d86246442a7"}\n'

def wsgi(env, start_response):
	print(env)
	if "HTTP_X_CSES_PATH" in env:
		env["PATH_INFO"] = env["HTTP_X_CSES_PATH"]
		del env["HTTP_X_CSES_PATH"]
	else:
		env["PATH_INFO"] = "/"
	
	def my_start_response(status, headers):
		modheaders = []
		varymodified = False
		for h in headers:
			if h[0] == "Vary":
				if h[1]:
					h = "Vary", h[1]+",X-CSES-Path"
				else:
					h = "Vary", "X-CSES-Path"
				varymodified = True
			
			modheaders.append(h)
		
		if not varymodified:
			modheaders.append(("Vary", "X-CSES-Path"))
		
		return start_response(status, modheaders)
	
	return api.app(env, my_start_response)

@api.app.route("/corstunnel")
def corstunnel(app, req):
	return wsgi
