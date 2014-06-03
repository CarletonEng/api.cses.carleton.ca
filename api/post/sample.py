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
from api.person import Person
from api.post import Post

sess = db.Session()

def post(id, title, content, type=None):
	p = Post()
	sess.add(p)
	p.id = id
	p.title = title
	p.content = content
	if type:
		p.type = type
	return p

post("hello-world", "Hello, World!", "<p>This is a post!</p>")
post("first-post", "I am awesome", "<p>f1rs+ p0$t n00b5</p>")
post("irontimes/", "Iron Times", "homepage")
post("irontimes/authors", "Iron Times Authors", "<ul><li>someone</li><li>someone else</li></ul>")

sess.commit()
