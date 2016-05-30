#!/usr/bin/python

import pymongo
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, json, request, render_template, abort, Response

app = Flask(__name__)
app.config.update(
	PROPAGATE_EXCEPTIONS = True
)


postitCollection = MongoClient().postit.postits

# Test for empty string
IsNullOrEmpty = lambda s: True if s and s.strip() else False

@app.errorhandler(404)
def page_not_found(e):
    return render_template('_404.html'), 404

@app.route('/')
def home():
	view = []
	for postit in postitCollection.find().sort('_id', -1):
		id = str(postit['_id'])
		title = postit['title']
		content = postit['content']
		content = content.replace('\n', '<br />')
		content = re.sub(r'#([a-zA-Z0-9]+)', r'<a href="/h/\1">#\1</a>', content)
		content = re.sub(r'(((https?|ftp)://|www.)[^\s<]+[^\s<\.)])', r'<a href="\1">\1</a>', content)
		post = {
			'title': title,
			'content': content,
			'id': id
		}
		view.append(post)
	
	return render_template('_postit.html', view = view)

@app.route('/h/<hash>')
def get_hash(hash = None):
	view = []
	for postit in postitCollection.find({ 'tags' : { '$elemMatch' : { '$regex' : hash, '$options' : 'i' }}}).sort('_id', -1):
		id = str(postit['_id'])
		title = postit['title']
		content = postit['content']
		content = content.replace('\n', '<br />')
		content = re.sub(r'#([a-zA-Z0-9]+)', r'<a href="/h/\1">#\1</a>', content)
		content = re.sub(r'(((https?|ftp)://|www.)[^\s<]+[^\s<\.)])', r'<a href="\1">\1</a>', content)
		post = {
			'id': id,
			'title': title,
			'content': content
		}
		view.append(post)
	
	return render_template('_postit.html', view = view)

@app.route('/s/<id>')
def get_submit(id = None):
	_id = ()
	try:
		_id = ObjectId(id)
	except:
		abort(404)
	
	postit = postitCollection.find_one({'_id': _id})
	if postit is None:
		abort(404)
		
	id = str(postit['_id'])
	title = postit['title']
	content = postit['content']
	content = content.replace('\n', '<br />')
	content = re.sub(r'#([a-zA-Z0-9]+)', r'<a href="/h/\1">#\1</a>', content)
	content = re.sub(r'(((https?|ftp)://|www.)[^\s<]+[^\s<\.)])', r'<a href="\1">\1</a>', content)
	view = {
		'id': id,
		'title': title,
		'content': content
	}
	
	return render_template('_one.html', view = view)
	
@app.route('/submit', methods = ['GET'])
def create_submit():
	return render_template('_submit.html')
	
@app.route('/submit', methods = ['POST'])
def post_submit():
	r = request.json
	if r is not None:
		#title = re.sub('<[^<]+?>', '', r['title'])
		#content = re.sub('<[^<]+?>', '', r['content'])
		title = r['title'].replace('<', '&lt;').replace('>', '&gt;')
		content = r['content'].replace('<', '&lt;').replace('>', '&gt;')
		if IsNullOrEmpty(title) is not False:
			tags = re.findall(r'#([a-zA-Z0-9]+)', r['content'])
			postit = {
				'title': title,
				'content': content,
				'tags': tags
			}
			postitCollection.insert(postit)
	
			return json.dumps({})
	
	return json.dumps({}), 404
	
@app.route('/edit/<id>', methods = ['GET'])
def get_edit(id	= None):
	_id = ()
	try:
		_id = ObjectId(id)
	except:
		abort(404)
	
	postit = postitCollection.find_one({'_id': _id})
	if postit is None:
		abort(404)
	
	view = {
		'id': str(postit['_id']),
		'title': postit['title'],
		'content': postit['content']
	}
	
	return render_template('_edit.html', view = view)
	
@app.route('/edit/<id>', methods = ['POST'])
def post_edit(id = None):
	_id = ()
	try:
		_id = ObjectId(id)
	except:
		abort(404)
	
	r = request.json
	if r is not None:
		#title = re.sub('<[^<]+?>', '', r['title'])
		#content = re.sub('<[^<]+?>', '', r['content'])
		title = r['title'].replace('<', '&lt;').replace('>', '&gt;')
		content = r['content'].replace('<', '&lt;').replace('>', '&gt;')
		if IsNullOrEmpty(title) is not False:
			tags = re.findall(r'#([a-zA-Z0-9]+)', r['content'])
			postit = {
				'title': title,
				'content': content,
				'tags': tags
			}
			postitCollection.update({ '_id': _id }, { '$set': postit })
			
			return json.dumps({})
			
	return json.dumps({}), 404

@app.route('/api/s/list')
def api_list_submits():
	view = []
	for postit in postitCollection.find().sort('_id', 0):
		post = {
			'id': str(postit['_id']),
			'title': postit['title'],
			'content': postit['content']
		}
		view.append(post)
	
	return Response(json.dumps(view), mimetype='application/json')
	
def prepare():
	title = r['title'].replace('<', '&lt;').replace('>', '&gt;')
	content = r['content'].replace('<', '&lt;').replace('>', '&gt;')
	content = content.replace('\n', '<br />')
	content = re.sub(r'#([a-zA-Z0-9]+)', r'<a href="/h/\1">#\1</a>', content)
	content = re.sub(r'(((https?|ftp)://|www.)[^\s<]+[^\s<\.)])', r'<a href="\1">\1</a>', content)
		
if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 8080, debug = True)

