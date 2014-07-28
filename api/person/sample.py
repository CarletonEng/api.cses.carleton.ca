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

k = person(999123456, "Kevin", "Kevin Cox", "passwd",
           ["selfw","selfr","personr","personw","upload","tbt"])
sess.add(Email(user=k, email="kevincox@kevincox.ca"))
person(999000000, "Jane", "Jane Smith", "enaj", ["selfr","selfw","tbt"])
person(999111111, "John", "John Doe", "password1", ["selfr","selfw"])
person(999222222, "Jason Grey", "Jason Grey", "topsecret", ["selfr","selfw"])

sess.commit()
