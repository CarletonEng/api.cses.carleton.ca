import api.db as db
from api.person import Person, Email

sess = db.Session()

def person(id, name, full, pw, perms):
	p = Person(number=id,
	           name=name,
	           namefull=full,
	           perms=perms)
	p.password_set(pw)
	sess.add(p)
	return p

kevin = person(999123456,"Kevin", "Kevin Cox", "passwd",
               ["selfw","selfr","personr","personw","upload",
                "tbt","postw","wheel", "mailinglist"])
person(999000000, "Jane", "Jane Smith", "enaj",
       ["selfr","selfw","tbt"])
person(999111111, "John", "John Doe", "password1",
       ["selfr","selfw","postw"])
person(999222222, "Jason Grey", "Jason Grey", "topsecret",
       ["selfr","selfw"])
person(999222232, "Support", "Support desk", "5",
                 ["selfr","selfw","personr","personw"])

sess.add(Email(user=kevin, email="kevincox@kevincox.ca"))

sess.commit()
