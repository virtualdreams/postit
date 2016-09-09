#!/usr/bin/python

import pymongo
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, json, request, redirect, url_for, render_template, abort, Response
from flask.ext.login import LoginManager
from flask.ext.login import login_user, logout_user, current_user, login_required, UserMixin
from database import Postit
from user import User

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
db = Postit()

# Test for empty string
IsNullOrEmpty = lambda s: True if s and s.strip() else False

# all routes goes here
@login.user_loader
def load_user(id):
	print 'load_user -> <%s>' % id
	return User.get(id)

#@app.before_request
#def before_request():
#	print current_user.is_authenticated()
	
@app.route('/logout')
def logout():
	logout_user()
	
	return redirect('/')
	
@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('_login.html')
	
	r = request.json
	if r is not None:
		user = User.get(r.get('username'))
		print 'login -> <%s>' % user
		if user is not None and user.authenticate(r.get('password')):
			login_user(user)
			return json.dumps({})

	abort(500)
	
@app.errorhandler(404)
def page_not_found(e):
    return render_template('_404.html'), 404

@app.route('/')
#@login_required
def home():
	_result = db.get_all()
	
	return render_template('_postit.html', view = _result)

# get submits by hash/tag
@app.route('/h/<hash>')
def get_hash(hash = None):
	_result = db.getByHash(hash)

	return render_template('_postit.html', view = _result)

# get submit by id
@app.route('/s/<id>')
def get_submit(id = None):
	_result = db.getById(id)
	if not _result:
		abort(404)
	
	return render_template('_one.html', view = _result)

# create a submit
@app.route('/submit', methods = ['GET', 'POST'])
@login_required
def submit():
	if request.method == 'GET':
		return render_template('_submit.html')
	
	r = request.json
	if r is not None:
		_result = db.add_submit(r.get('title'), r.get('content'), current_user.get_myid())
		if _result is not None:
			return json.dumps({})
			
	return json.dumps({'error': '500'}), 500

# edit a submit	
@app.route('/submit/<id>', methods = ['GET', 'POST'])
@login_required
def edit(id	= None):
	_result = db.getById(id, True)
	if not _result:
		abort(404)

	if request.method == 'GET':
		return render_template('_edit.html', view = _result)

	r = request.json
	if r is not None:
		_result = db.update_submit(id, r.get('title'), r.get('content'))
		if _result:
			return json.dumps({})
		
	return json.dumps({}), 500

# search for keywords
@app.route('/search/<term>', methods = ['GET'])
def get_search(term = None):
	if term is None:
		abort(404)
	
	_result = db.search(term)
	
	return render_template('_postit.html', view = _result)

# add a comment to a submit
@app.route('/c', methods = ['POST'])
@login_required
def post_comment(id = None):
	if current_user.is_authenticated():
		r = request.json
		if r is not None:
			_result = db.add_comment(r.get('id'), r.get('content'), current_user.get_myid())
			if _result is not None:
				return json.dumps({})
	
	return json.dumps({}), 500

'''
@app.route('/api/s/list')
def api_list_submits():
	_result = db.getAll()
	
	return Response(json.dumps(list(_result)), mimetype='application/json')
'''

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 8082, debug = True)

