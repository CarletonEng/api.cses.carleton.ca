from datetime import datetime

import api
from api import db

class Post(db.Base):
	""" A post.
		
		Instance Attributes:
			id:
				A string containing a unique hex ID representing the post.
			type:
				The type of document this is.  Can be one of the following:
				- "article": This is a timed "blog-like" post.
				- "page": This is a page.
			content:
				The HTML content of the page.
			perms:
				If false this post is public.  Otherwise a list of permissions
				that can view this post.
	"""
	
	__tablename__ = 'post'
	
	_id     = db.Column("id", db.String, primary_key=True, nullable=False)
	# _dir    = db.Column("dir", db.String, nullable=False)
	type    = db.Column(db.String, default=lambda:"page", server_default="page", nullable=False)
	created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
	title   = db.Column(db.StringStripped, nullable=False)
	content = db.Column(db.String, nullable=False);
	perms   = db.Column(db.JSON)
	
	@db.hybrid_property
	def id(self):
		return self._id
	
	@id.setter
	def id(self, v):
		self._id  = v
		# self._dir, _, _ = v.rpartition("/")
	
	@db.hybrid_property
	def directory(self):
		return self._dir
	
	def __repr__(self):
		return api.autorepr(self, self.id, self.type)

db.Index("post_created_idx", Post.type, Post.created, Post._id)
