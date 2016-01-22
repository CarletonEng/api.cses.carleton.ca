import api.db as db
from api.auth import Auth
from api.person import Person

import api.person.sample

sess = db.Session()

def auth(uid, tok, perms=None):
	id, _, pw = tok.partition("$")
	p = sess.query(Person).get(uid)
	a = Auth(p)
	a.neverusethisinsecuremethod_set(id,pw)
	a.perms = p.perms if perms is None else perms
	sess.add(a)
	return a

auth("1", "11$pw11")
auth("1", "12$pw12", ["selfr", "selfw"])
auth("2", "2$pw2")
auth("3", "3$pw3")

sess.commit()
