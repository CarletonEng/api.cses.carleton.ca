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
from api.banner import Banner, BannerImage

sess = db.Session()

sess.add(Banner(alt="CSES!", images=[
	BannerImage(blob="BF263BDFE95CBD9101C3AE769B2F93A10AE576D6", width=619, height=183),
	BannerImage(blob="12DC7B0D61D0943E0E862A55911ABA43619EA371", width=200, height=200),
]))

sess.add(Banner(alt="Summer Directorship Applications Now Open", href="/directorships", images=[
	BannerImage(blob="B963C4AEE97D58F264B62E5F61E7829DEA94332F", width=647, height=253),
]))

sess.commit()
