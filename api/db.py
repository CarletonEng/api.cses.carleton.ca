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

import math
import json
from binascii import hexlify, unhexlify

import sqlalchemy
from sqlalchemy import Column, Boolean, Integer, String, BINARY, ForeignKey, DateTime
from sqlalchemy import Index
from sqlalchemy.exc import StatementError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, reconstructor, relationship, backref
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func, expression

import api
from api import app

engine  = sqlalchemy.create_engine(app.config.database, echo=app.config.debug)
Base    = declarative_base()
Session = sessionmaker(bind=engine)

class Hex(TypeDecorator):
	""" A hex column type
		
		This column stores its value in the database as an integer but is set
		and retrieved by the application as hex strings.  This is intended for
		object IDs that will be presented in locations such as URLs.
		
		This column acts as an integer in all ways except for the conversion
		to and from hex upon access, this includes the ability for
		auto-incrementing keys.
	"""
	impl = Integer
	
	def process_bind_param(self, value, dialect):
		try:    return int(value, 16) if value is not None else None
		except: return None
	
	def process_result_value(self, value, dialect):
		return format(int(value), "X") if value is not None else None

class HexLong(TypeDecorator):
	""" A long hex column
		
		This has the same interface as the Hex column except that it stores its
		result as a binary string rather than an integer.  This allows for
		storage of longer strings but loses the ability to act as an integer
		such as auto-increment.
	"""
	impl = BINARY
	
	def __init__(self, length=None):
		if length:
			length = math.ciel(length//8) # Convert bits to bytes.
		
		super().__init__(length)
	
	def process_bind_param(self, value, dialect):
		if len(value) % 2:
			value = "0"+value
		
		try:    return unhexlify(value)
		except: return None
	
	def process_result_value(self, value, dialect):
		return hexlify(value).decode().upper()

class JSON(TypeDecorator):
	impl = String
	
	def __init__(self, *args, sort=False, **kwargs):
		super().__init__(*args, **kwargs)
		self.__sort = sort
	
	def process_bind_param(self, value, dialect):
		return json.dumps(value, separators=(",", ":"), sort_keys=self.__sort)
	
	def process_result_value(self, value, dialect):
		return value and json.loads(value)

class ListSorted(JSON):
	def process_bind_param(self, value, dialect):
		value.sort()
		return super().process_bind_param(value, dialect)

class StringStripped(TypeDecorator):
	impl = String
	
	def process_bind_param(self, value, dialect):
		return value and value.strip()
	
	def process_result_value(self, value, dialect):
		return value
