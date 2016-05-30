#!/usr/bin/python

import pymongo
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, json, request, render_template, abort, Response
from database import PostitDb

app = Flask(__name__)
app.config.update(
	PROPAGATE_EXCEPTIONS = True
)

# postit database
postitCollection = MongoClient().postit.postits

db = PostitDb()

# Test for empty string
IsNullOrEmpty = lambda s: True if s and s.strip() else False

@app.errorhandler(404)
def page_not_found(e):
    return render_template('_404.html'), 404

@app.route('/')
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
		
#@app.route('/api/s/list')
#def api_list_submits():
#	view = []
#	for postit in postitCollection.find().sort('_id', 0):
#		post = {
#			'id': str(postit['_id']),
#			'title': postit['title'],
#			'content': postit['content']
#		}
#		view.append(post)
#	
#	return Response(json.dumps(view), mimetype='application/json')
		
if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 8081, debug = True)

