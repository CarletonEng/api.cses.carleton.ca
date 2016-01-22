import os.path

from api import db
from api.blob import Blob

sess = db.Session()

def blob(mime, content):
	b = Blob(mime=mime)
	b.write(content)
	sess.add(b)
	return b

def file(mime, name):
	name = os.path.join(os.path.dirname(__file__), name)
	b = Blob(mime=mime)
	b.writestream(open(name, "rb"))
	sess.add(b)
	return b

# 99E9CFEF7680554C6E705C8B723D6563381B12FB
blob("text/plain; charset=utf8", [b"Hello, I am a blob.\n"])

file("image/png", "sample/cses.png")
file("image/png", "sample/cses-small.png")
file("image/png", "sample/Banner1.jpg")

sess.commit()
