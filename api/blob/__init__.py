import os
import string
import random
from hashlib import sha1
import zlib

from werkzeug.wsgi import wrap_file

import api
from api import app, db

class Blob(db.Base):
	""" A blob.
		
		Instance Attributes:
			id:
				The SHA1 hash of the data.
			mime:
				The mime type of the data.
	"""
	
	__tablename__ = 'blob'
	
	id   = db.Column(db.HexLong, primary_key=True)
	mime = db.Column(db.StringStripped, default=lambda:"application/octet-stream")
	enc  = db.Column(db.StringStripped)
	perm = db.Column(db.JSON, default=lambda: False)
	
	datapath = os.path.join(app.config.datapath, "blobs/")
	
	def __init__(self, *, mime="application/octet-stream"):
		super().__init__()
		self.__always_init()
		
		self.mime = mime
	
	@db.reconstructor
	def __always_init(self):
		self.__statcache = None
	
	@property
	def has_hash(self):
		return bool(self.id)
	
	@property
	def path(self):
		self.__mkdirs()
		return Blob.datapath + self.id[:2]+"/"+self.id[2:]
	
	def __tmppath(self):
		os.makedirs(Blob.datapath, 0o775, exist_ok=True)
		return Blob.datapath + hex(random.getrandbits(32)) + ".tmp"
	
	@property
	def stat(self):
		if not self.__statcache:
			self.__statcache = os.stat(self.path)
		return self.__statcache
	
	@property
	def size(self):
		return self.stat.st_size
	
	@property
	def exists(self):
		return self.has_hash and os.path.isfile(self.path)
	
	def open(self):
		return open(self.path, "rb")
	
	def __mkdirs(self):
		os.makedirs(Blob.datapath+self.id[:2], 0o755, exist_ok=True)
	
	def write(self, content):
		if self.id:
			tmp = self.path
		else:
			tmp = self.__tmppath()
		
		if self.exists:
			raise TypeError("File already exists")
		
		with open(tmp, "xb") as f:
			if isinstance(content, bytes):
				content = content,
			content = iter(content)
			
			h = sha1()
			c = None
			
			# Is compression worth while?
			first = next(content, "")
			# Subtract 8 to avoid counting header/footer.
			ratio = (len(zlib.compress(first))-8)/len(first)
			if ratio < 0.98:
				c = zlib.compressobj(level=9, wbits=15|0x10) # Gzip format.
				self.enc = "gzip"
			
			def add(s):
				h.update(s)
				if c:
					s = c.compress(s)
				f.write(s)
			
			add(first)
			for s in content:
				add(s)
			
			if c:
				s = c.flush()
				f.write(s)
		
		nh = h.hexdigest().upper()
		if self.id and self.id != nh:
			os.remove(tmp)
			raise TypeError("Hash Incorrect")
		
		self.id = nh
		os.rename(tmp, self.path)
	
	def writestream(self, s):
		return self.write(Blob.chunked(s))
	
	@staticmethod
	def chunked(s, size=60*1024):
		while True:
			r = s.read(64*1024)
			if r:
				yield r
			else:
				break
	
	def __repr__(self):
		return api.autorepr(self, self.id)
