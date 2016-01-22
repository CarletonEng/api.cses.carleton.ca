#! /usr/bin/env python3

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
