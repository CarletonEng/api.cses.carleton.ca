from datetime import datetime

import api.db as db
from api.person import Person
from api.post import Post

sess = db.Session()

def post(id, title, content, **kwargs):
	p = Post(id=id, title=title, content=content, **kwargs)
	sess.add(p)
	return p

post("services", "Hello, World!", "<p>This is a post!</p>")
post("publications", "I am awesome", "<p>f1rs+ p0$t n00b5</p>")
post("publications/irontimes", "Iron Times", "<p>homepage</p>foo<p>bar</p>")
post("publications/irontimes/authors", "Iron Times Authors", "<ul><li>someone</li><li>someone else</li></ul>")

post("1994/09/14/birthday", "Happy Birthday",
     "<p>Today the author was born.</p>",
     created=datetime(1994,9,14), type="article")
post("2014/09/01/engfrosh", "Start of EngFrosh",
     "<p>Welcome to EngFrosh!</p>",
     created=datetime(2014,9,1), type="article")
post("2014/09/13/tbt", "Textbook Trade",
     "<p>The textbook trade is now open!</p>",
     created=datetime(2014,9,13), type="article")
post("3000/01/01/from-future", "Dear Past",
     "<p>Hello, this is a message from the future.</p>",
     created=datetime(3000,1,1), type="article")

sess.commit()
