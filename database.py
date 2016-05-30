from pymongo import MongoClient
from bson.objectid import ObjectId
import re

class PostitDb():
	def __init__(self):
		self.collection = MongoClient().postit.postits
		
	def add(self, title, content):
		if title and content:
			post = {
				'title': title,
				'content': content,
				'tags': re.findall(r'#([a-zA-Z0-9]+)', content)
			}
			self.collection.insert(post)
			return post.get('_id')
		else:
			return None
		
	def update(self, id, title, content):
		_id = ()
		try:
			_id = ObjectId(id)
		except:
			return False
		
		if title and content:
			post = {
				'title': title,
				'content': content,
				'tags': re.findall(r'#([a-zA-Z0-9]+)', content)
			}
			self.collection.update({'_id': _id}, { '$set': post })
			return True
		
		return False
		
	def getAll(self):
		for postit in self.collection.find().sort('_id', -1):##.skip(5).limit(5):
			# get the values
			_title = postit.get('title')
			_content = postit.get('content')
			
			# sanitizing
			_title = self._sanitize(_title)
			_content = self._sanitize(_content)
			
			# replace links and hashes
			_content = self._prepare(_content)
			
			# create the object
			post = {
				'id': str(postit.get('_id')),
				'title': _title,
				'content': _content
			}
			yield post
		
	def getById(self, id, raw = False):
		_id = ()
		try:
			_id = ObjectId(id)
		except:
			return None
			
		postit = self.collection.find_one({'_id': _id})
		if not postit:
			return None
		
		_title = postit.get('title')
		_content = postit.get('content')
		
		if not raw:
			# sanitizing
			_title = self._sanitize(_title)
			_content = self._sanitize(_content)
			
			# replace links and hashes
			_content = self._prepare(_content)
		
		# create the object
		post = {
			'id': str(postit.get('_id')),
			'title': _title,
			'content': _content
		}
		return post
		
	def getByHash(self, hash):
		for postit in self.collection.find({ 'tags' : { '$elemMatch' : { '$regex' : hash, '$options' : 'i' }}}).sort('_id', -1):
			# get the values
			_title = postit.get('title')
			_content = postit.get('content')
			
			# sanitizing
			_title = self._sanitize(_title)
			_content = self._sanitize(_content)
			
			# replace links and hashes
			_content = self._prepare(_content)
			
			# create the object
			post = {
				'id': str(postit.get('_id')),
				'title': _title,
				'content': _content
			}
			yield post
			
	def search(self, term):
		terms = term.split()
		x = []
		for t in terms:
			s = {
				'content': { '$regex': t, '$options': 'i' }
			}
			x.append(s)
			
		print x
			
		for postit in self.collection.find({'$or': x}).sort('_id', -1):
			# get the values
			_title = postit.get('title')
			_content = postit.get('content')
			
			# sanitizing
			_title = self._sanitize(_title)
			_content = self._sanitize(_content)
			
			# replace links and hashes
			_content = self._prepare(_content)
			
			# create the object
			post = {
				'id': str(postit.get('_id')),
				'title': _title,
				'content': _content
			}
			yield post
		
	def _sanitize(self, value):
		return value.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br />')
		
	def _prepare(self, value):
		_value = value
		_value = re.sub(r'#([a-zA-Z0-9]+)', r'<a href="/h/\1">#\1</a>', _value)
		_value = re.sub(r'(((https?|ftp)://|www.)[^\s<]+[^\s<\.)])', r'<a href="\1">\1</a>', _value)
		return _value
