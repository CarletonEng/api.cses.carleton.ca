import pytest

from api import db, tbtbook

@pytest.fixture
def book():
	return {
		"authorizer": 1,
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
	
	book["authorizer"] = 3
	r = wtapp.put_json("/tbt/book", book, headers=authas(1), expect_errors=True)
	assert r.status_code == 403
	assert r.json["e"] == 1
	assert "Authorizer is not allowed to make changes." in r.json["msg"]
	assert "tbt" in r.json["msg"]

def test_update_book_authorization(wtapp, authas, book):
	r = wtapp.put_json("/tbt/book/1", book, expect_errors=True)
	assert r.status_code == 401
	assert r.json["e"] == 1
	
	r = wtapp.put_json("/tbt/book/1", book, headers=authas(3), expect_errors=True)
	assert r.status_code == 403
	assert r.json["e"] == 1
	assert r.json["msg"] == "You are not allowed."
	
	book["authorizer"] = 3
	r = wtapp.put_json("/tbt/book/1", book, headers=authas(1), expect_errors=True)
	assert r.status_code == 403
	assert r.json["e"] == 1
	assert "Authorizer is not allowed to make changes." in r.json["msg"]
	assert "tbt" in r.json["msg"]

def test_delete_book_authorization(wtapp, authas, book):
	r = wtapp.put_json("/tbt/book", book, headers=authas(1))
	book = "/tbt/book/{}".format(r.json["id"])
	
	r = wtapp.delete_json(book, expect_errors=True)
	assert r.status_code == 401
	assert r.json["e"] == 1
	
	r = wtapp.delete_json(book, headers=authas(3), expect_errors=True)
	assert r.status_code == 403
	assert r.json["e"] == 1
	assert r.json["msg"] == "You are not allowed. ('tbt' permission required.)"

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

def test_create_change_log(wtapp, authas, book, sess):
	headers = authas(1)
	
	r = wtapp.put_json("/tbt/book", book, headers=headers)
	book = "/tbt/book/{}".format(r.json["id"])
	
	wtapp.put_json(book, {
		"authorizer": 1,
		"buyer": 2,
	}, headers=headers)
	
	wtapp.put_json(book, {
		"authorizer": 2,
		"paid": True,
	}, headers=headers)
	
	r = wtapp.get(book, headers=headers)
	assert r.json == {"e": 0,
		"author": "The Author",
		"buyer": 2,
		"courses": [],
		"edition": "",
		"paid": True,
		"price": 4325,
		"seller": 2,
		"title": "A Book",
	}
	
	r = wtapp.get(book+"/changes", headers=headers)
	changes = r.json["changes"]
	
	assert len(changes) == 3
	
	assert changes[0]["by"] == 1
	assert "created" in changes[0]["desc"]
	
	assert changes[1]["by"] == 1
	assert "sold book" in changes[1]["desc"]
	
	assert changes[2]["by"] == 2
	assert "paid buyer" in changes[2]["desc"]
