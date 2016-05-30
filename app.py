#!/usr/bin/python

import pymongo
import re
from pymongo import MongoClient
from flask import Flask, json, request, render_template
from jinja2 import Markup

app = Flask(__name__)

postitCollection = MongoClient().postit.postits

@app.route('/')
def home():
	postits = []
	for postit in postitCollection.find().sort('_id', 0):
		content = postit['content']
		content = content.replace('\n', '<br />')
		content = re.sub(r'#([a-zA-Z0-9]+)', r'<a href="/h/\1">#\1</a>', content)
		content = re.sub(r'(((https?|ftp)://|www.)[^\s<]+[^\s<\.)])', r'<a href="\1">\1</a>', content)
		postit['content'] = content
		postits.append(postit)

	return render_template('_postit.html', postits = postits)

@app.route('/h/<hash>')
def hash(hash = None):
	postits = []
	for postit in postitCollection.find({ 'tags' : { '$elemMatch' : { '$regex' : hash, '$options' : 'i' }}}).sort('_id', 0):
		content = postit['content']
		content = re.sub(r'#([a-zA-Z0-9]+)', r'<a href="/h/\1">#\1</a>', content)
		content = re.sub(r'(((https?|ftp)://|www.)[^\s<]+[^\s<\.)])', r'<a href="\1">\1</a>', content)
		postit['content'] = content
		postits.append(postit)
	
	return render_template('_postit.html', postits = postits)
	
@app.route('/submit', methods = ['GET'])
def submit():
	return render_template('_submit.html')
	
@app.route('/submit', methods = ['POST'])
def submit_post():
	r = request.json
	if r is not None:
		tags = re.findall(r'#([a-zA-Z0-9]+)', r['content'])
		postit = {
			'title': r['title'],
			'content': r['content'],
			'tags': tags
		}
		postitCollection.insert(postit)
	
	return json.dumps({})
	
app.run(host = '0.0.0.0', port = 8080, debug = True)

