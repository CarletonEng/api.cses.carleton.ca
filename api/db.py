#! /usr/bin/env python3

import math
import json
from binascii import hexlify, unhexlify

import sqlalchemy
from sqlalchemy import Table, Column, Boolean, Integer, String, ForeignKey, \
    DateTime, CheckConstraint
from sqlalchemy import Index, event, LargeBinary
from sqlalchemy.exc import DatabaseError, StatementError, IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, reconstructor, relationship, backref
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func, expression

import sqlite3

import api
from api import app

engine = sqlalchemy.create_engine(app.config.database, echo=app.config.debug)

@event.listens_for(engine, "connect")
def initalizedb(dbapi_connection, connection_record):
	if isinstance(dbapi_connection, sqlite3.Connection):
		cursor = dbapi_connection.cursor()
		cursor.execute("PRAGMA foreign_keys=ON;")
		cursor.close()

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = sqlalchemy.MetaData(naming_convention=naming_convention)
Base    = declarative_base(metadata=metadata)
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
	impl = LargeBinary
	
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

def prefixof(col, s):
	e = s[:-1]+chr(ord(s[-1])+1)
	return (s <= col) & (col < e)
