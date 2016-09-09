from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import datetime

class Postit(object):
	def __init__(self):
		client = MongoClient()
		self.posts = client.postit.postits
		self.comments = client.postit.comments
		
	def add_submit(self, title, content, user):
		if title:
			post = {
				'owner': user,
				'title': title,
				'content': content,
				'tags': re.findall(r'/h/([a-zA-Z0-9]+)', content)
			}
			self.posts.insert(post)
			return post.get('_id')
		else:
			return None
		
	def update_submit(self, id, title, content):
		_id = ()
		try:
			_id = ObjectId(id)
		except:
			return False
		
		if title:
			post = {
				'title': title,
				'content': content,
				'tags': re.findall(r'/h/([a-zA-Z0-9]+)', content)
			}
			self.posts.update({'_id': _id}, { '$set': post })
			return True
		
		return False
		
	def add_comment(self, id, content, user):
		_id = ()
		try:
			_id = ObjectId(id)
		except:
			return None
			
		if content:
			comment = {
				'owner': user,
				'post': _id,
				'content': content
			}
			self.comments.insert(comment)
			return comment.get('_id')
		else:
			return None

	def update_comment(self, id, content):
		pass
		
	def get_all(self):
		for postit in self.posts.find().sort('_id', -1):##.skip(5).limit(5):
			# get the values
			_title = postit.get('title')
			_content = postit.get('content')
			
			# sanitizing
			_title = self._sanitize(_title)
			_content = self._sanitize(_content)
			
			# replace links and hashes
			_content = self._prepare(_content)
			
			# article age
			_now = datetime.datetime.utcnow()
			_age1, _age2 = self._age(postit.get('_id').generation_time, _now)
			_posted = self._agetoword(_age2)
			
			# comments
			_comments = self.getCommentsCount(str(postit.get('_id')))
			
			# create the object
			post = {
				'id': str(postit.get('_id')),
				'user': 'admin',
				'title': _title,
				'content': _content,
				'posted': _posted,
				'comments': _comments
			}
			yield post
		
	def getById(self, id, raw = False):
		_id = ()
		try:
			_id = ObjectId(id)
		except:
			return None
			
		postit = self.posts.find_one({'_id': _id})
		if not postit:
			return None
		
		_title = postit.get('title')
		_content = postit.get('content')
		
		if not raw:
			# sanitizing
			_title = self._sanitize(_title)
			_content = self._sanitize(_content)
			
			# replace links and hashes
			_title = self._prepare(_title)
			_content = self._prepare(_content)
			
		# article age
		_now = datetime.datetime.utcnow()
		_age1, _age2 = self._age(postit.get('_id').generation_time, _now)
		_posted = self._agetoword(_age2)
		
		# comments
		_comments = self.getCommentsCount(str(postit.get('_id')))
		
		# create the object
		post = {
			'id': str(postit.get('_id')),
			'title': _title,
			'content': _content,
			'posted': _posted,
			'comments_count': _comments,
			'comments': self.getComments(str(postit.get('_id')))
		}
		return post
		
	def getByHash(self, hash):
		for postit in self.posts.find({ 'tags' : { '$elemMatch' : { '$regex' : hash, '$options' : 'i' }}}).sort('_id', -1):
			# get the values
			_title = postit.get('title')
			_content = postit.get('content')
			
			# sanitizing
			_title = self._sanitize(_title)
			_content = self._sanitize(_content)
			
			# replace links and hashes
			_content = self._prepare(_content)
			
			# article age
			_now = datetime.datetime.utcnow()
			_age1, _age2 = self._age(postit.get('_id').generation_time, _now)
			_posted = self._agetoword(_age2)
			
			# create the object
			post = {
				'id': str(postit.get('_id')),
				'title': _title,
				'content': _content,
				'posted': _posted
			}
			
			yield post
			
	def search(self, term):
		terms = term.split()
		x = []
		for t in terms:
			s = {
				'$or': [
					{'title': { '$regex': t, '$options': 'i' }},
					{'content': { '$regex': t, '$options': 'i' }}
				]
			}
			x.append(s)
			
		# print x
			
		for postit in self.posts.find({'$or': x}).sort('_id', -1):
			# get the values
			_title = postit.get('title')
			_content = postit.get('content')
			
			# sanitizing
			_title = self._sanitize(_title)
			_content = self._sanitize(_content)
			
			# replace links and hashes
			_content = self._prepare(_content)
			
			# article age
			_now = datetime.datetime.utcnow()
			_age1, _age2 = self._age(postit.get('_id').generation_time, _now)
			_posted = self._agetoword(_age2)
			
			# create the object
			post = {
				'id': str(postit.get('_id')),
				'title': _title,
				'content': _content,
				'posted': _posted
			}
			yield post
			
	def getComments(self, id):
		_id = ()
		try:
			_id = ObjectId(id)
		except:
			yield []
		
		for comment in self.comments.find({'post': _id}).sort('_id', -1):
			# comment age
			_now = datetime.datetime.utcnow()
			_, _age2 = self._age(comment.get('_id').generation_time, _now)
			_posted = self._agetoword(_age2)
			
			# content
			_content = comment.get('content')
			
			# sanitizing
			_content = self._sanitize(_content)
			
			# replace links and hashes
			_content = self._prepare(_content)
			
			# create the object
			_comment = {
				'id': str(comment.get('_id')),
				'content': _content,
				'posted': _posted
			}
			
			yield _comment
			
	def getCommentsCount(self, id):
		_id = ()
		try:
			_id = ObjectId(id)
		except:
			return None
		
		return self.comments.find({'post': _id}).sort('_id', -1).count(True)
		
	def _sanitize(self, value):
		return value.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br />')
		
	def _prepare(self, value):
		_value = value
		
		_value = re.sub(r'/(h|u)/([a-zA-Z0-9]+)', r'<a href="/\1/\2">/\1/\2</a>', _value)
		_value = re.sub(r'(((https?|ftp)://|www.)[^\s<]+[^\s<\.)])', r'<a href="\1">\1</a>', _value)
		return _value
		
	def _age(self, created, now):
		_clean = created.replace(tzinfo = None)
		_diff = now - _clean
		
		_minutes = (_diff.days * 24 * 60) + (_diff.seconds / 60)
		
		return _diff, _minutes
		
	def _agetoword(self, minutes):
		if minutes < 60:
			return 'vor %s Minuten' % minutes
			
		if (minutes / 60) < 24:
			return 'vor %s Std.' % (minutes / 60)
			
		if (minutes / 60) >= 24 and (minutes / 60) < 48:
			return 'gestern'
			
		return 'vor %s Tagen' % ((minutes / 60) / 24)
			
		
