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

from os import path, environ as env
import os.path

import api

# The root of the code repository.
root = os.path.realpath(__file__+"/../../")+"/"

class Config:
	def __init__(s):
		s.debug    = bool(env.get("CSESAPI_DEBUG"))
		
		s.readonly     = bool(env.get("CSESAPI_READONLY"))
		s.readonly_tbt = bool(env.get("CSESAPI_READONLY_TBT"))
		
		s.datapath = env.get("CSESAPI_DATADIR", root+"cses-data/")
		s.database = env.get("CSESAPI_DB",      "sqlite:///"+s.datapath+"cses.sqlite")
	
	def __repr__(self):
		return api.autorepr(self, **self.__dict__)
		r = ["Config(", ")"]
		r[1:1] = ",\n       ".join(k+"="+repr(v) for k,v in self.__dict__.items())
		return "".join(r)
