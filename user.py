import pymongo
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask.ext.login import UserMixin

# User
class User(UserMixin):
	def __init__(self, username):
		self.users = MongoClient().postit.users
		self.username = username

	@staticmethod
	def get(username):
		users = MongoClient().postit.users
		_user = users.find_one({'username': username})
		print 'MongoDB <%s>' % _user
		if _user is not None:
			return User(username)

		return None

	def authenticate(self, password):
		user = self.users.find_one({'username': self.username})
		if user is not None and user.get('password') == password:
			return True

		return False

	def get_myid(self):
		user = self.users.find_one({'username': self.username})
		if user is not None:
			return user.get('_id')

		return None
	
	''' flask login methods '''
	def is_authenticated(self):
		return True
		
	def is_active(self):
		return True
		
	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.username)

	def __repr__(self):
		return 'User() -> <%s>' % self.username