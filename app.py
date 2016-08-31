#!/usr/bin/python

import pymongo
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, json, request, redirect, url_for, render_template, abort, Response
from flask.ext.login import LoginManager
from flask.ext.login import login_user, logout_user, current_user, login_required
from database import PostitDb

# init flask
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config.update(
	PROPAGATE_EXCEPTIONS = True
)

# login manager
login = LoginManager()
login.init_app(app)
login.login_view = 'login'
login.session_protection = None

# init database
db = PostitDb()

# Test for empty string
IsNullOrEmpty = lambda s: True if s and s.strip() else False

# User
class User(object):
	def __init__(self):
		pass
		
	def is_authenticated(self):
		return True
		
	def is_active(self):
		return True
		
	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode('admin')

# all routes goes here
@login.user_loader
def load_user(id):
	print 'load_user: %s' % id

	return User()

@app.before_request
def before_request():
	print current_user.is_authenticated()
	
@app.route('/logout')
def logout():
	logout_user()
	
	return redirect('/')
	
@app.route('/login')
def login():
	user = User()
	login_user(user)
	
	return redirect('/')
	
@app.errorhandler(404)
def page_not_found(e):
    return render_template('_404.html'), 404

@app.route('/')
#@login_required
def home():
	_result = db.getAll()
	
	return render_template('_postit.html', view = _result)

@app.route('/h/<hash>')
def get_hash(hash = None):
	_result = db.getByHash(hash)

	return render_template('_postit.html', view = _result)

@app.route('/s/<id>')
def get_submit(id = None):
	_result = db.getById(id)
	if not _result:
		abort(404)
	
	return render_template('_one.html', view = _result)
	
@app.route('/submit', methods = ['GET'])
def create_submit():
	return render_template('_submit.html')
	
@app.route('/submit', methods = ['POST'])
def post_submit():
	r = request.json
	if r is not None:
		_result = db.add(r.get('title'), r.get('content'))
		if _result is not None:
			return json.dumps({})
			
	return json.dumps({}), 500
	
@app.route('/edit/<id>', methods = ['GET'])
def get_edit(id	= None):
	_result = db.getById(id, True)
	if not _result:
		abort(404)
	
	return render_template('_edit.html', view = _result)
	
@app.route('/edit/<id>', methods = ['POST'])
def post_edit(id = None):
	r = request.json
	if r is not None:
		_result = db.update(id, r.get('title'), r.get('content'))
		if _result:
			return json.dumps({})
		
	return json.dumps({}), 500
	
@app.route('/search/<term>', methods = ['GET'])
def get_search(term = None):
	if term is None:
		abort(404)
	
	_result = db.search(term)
	
	return render_template('_postit.html', view = _result)

@app.route('/c/<id>', methods = ['POST'])
def post_comment(id = None):
	r = request.json
	if r is not None:
		_result = db.addComment(id, r.get('content'))
		if _result is not None:
			return json.dumps({})
	
	return json.dumps({}), 500

@app.route('/api/s/list')
def api_list_submits():
	_result = db.getAll()
	
	return Response(json.dumps(list(_result)), mimetype='application/json')
		
if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 8082, debug = True)

