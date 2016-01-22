import pytest

from api import db, tbtbook

@pytest.fixture
def book():
	return {
		"authorizer": "1",
		"title": "A Book",
		"author": "The Author",
		"price": 4325,
		"courses": [],
		"seller": "2",
	}

def test_create_book_authorization(wtapp, authas, book):
	r = wtapp.put_json("/tbt/book", book, expect_errors=True)
	assert r.status_code == 401
	assert r.json["e"] == 1
	
	r = wtapp.put_json("/tbt/book", book, headers=authas(3), expect_errors=True)
	assert r.status_code == 403
	assert r.json["e"] == 1
	assert r.json["msg"] == "Permission denied."

def test_create_book(wtapp, authas, book):
	wtapp.put_json("/tbt/book", book, headers=authas(1))

def test_course_validation(wtapp, authas, book, sess):
	book["courses"] = ["eCo r-1(01)0"];
	r = wtapp.put_json("/tbt/book", book, headers=authas(1))
	b = sess.query(tbtbook.TBTBook).get(r.json["id"])
	assert [c.code for c in b.courses] == ["ECOR1010"]
	
	book["courses"] = ["ABCD123"];
	r = wtapp.put_json("/tbt/book", book, headers=authas(1), expect_errors=True)
	assert r.status_code == 400
	assert r.json["e"] == 1
	assert "course code" in r.json["msg"]
	
	book["courses"] = ["ABC0123"];
	r = wtapp.put_json("/tbt/book", book, headers=authas(1), expect_errors=True)
	assert r.status_code == 400
	assert r.json["e"] == 1
	assert "course code" in r.json["msg"]
	
	book["courses"] = ["QWER1234", "invalid", "POIU0987"];
	r = wtapp.put_json("/tbt/book", book, headers=authas(1), expect_errors=True)
	assert r.status_code == 400
	assert r.json["e"] == 1
	assert "course code" in r.json["msg"]
