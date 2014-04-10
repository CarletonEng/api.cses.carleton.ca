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
from api.auth import Auth
from api.person import Person

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
