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
from api.tbtbook import TBTBook, TBTBookChange, Course

sess = db.Session()

def book(owner, title, author, price, courses, **kwargs):
	b = TBTBook(seller=owner,
	            title=title,
	            author=author,
	            price=price,
	            courses=courses,
	            **kwargs)
	sess.add(b)
	return b

kevin = sess.query(Person).get("1")
jane  = sess.query(Person).get("2")
john  = sess.query(Person).get("3")
print(kevin, jane, john)

b = book(kevin, "ECOR 1010 Fun Facts", "Kevin Cox", 100, ["ECOR1010"], edition="392th")
sess.add(TBTBookChange(book=b, user=kevin, desc="added \n"+repr(b)))

b = book(kevin, "The C Programming Language", "Dennis Ritchie", 1000, ["ECOR 1005", "SYSC-2001"])
sess.add(TBTBookChange(book=b, user=jane, desc="added \n"+repr(b)))

b = book(john, "Guide to Engineering", "Dr. Seuss", 10000, ["ECOR1010", "FOOB1234"], buyer=kevin)
sess.add(TBTBookChange(book=b, user=jane, desc="added \n"+repr(b)))

sess.commit()
