from google.appengine.ext import ndb

class UserProfile(ndb.Model):
	"""Models the profile (JSON) of an individual user."""
	# email is the key for each user.
	email = ndb.TextProperty(required=True)
	fname = ndb.StringProperty(required=True)
	lname = ndb.StringProperty(required=True)
	photoUrl = ndb.StringProperty()
	profile = ndb.TextProperty() # JSON file with user's profile info.
	date = ndb.DateTimeProperty(auto_now_add=True)

	@classmethod
	def getFromGAE(cls, appEngineUser):
		return cls.get_by_id(appEngineUser.email())

	@classmethod
	def getFromEmail(cls, email):
		return cls.get_by_id(email)

	@classmethod
	def getJsonFields(cls):
		return ['fname', 'lname', 'city_state', 'country',
		'facebook', 'twitter', 'github', 'linkedin',
		'year_experience', 'sector_experience', 'experience', 'demand', 'offer']

class UserSnippet(ndb.Model):
	"""NDB model for a user weekly snippet.
		Since we are in a given domain, we will use the login name as the key.
		`arnaud@thegovlab.org` will have `arnaud` as the key.
	"""
	content = ndb.TextProperty()

class Project(ndb.Model):
	"""NDB model for a project."""
	#shortName = ndb.StringProperty(required=True)
	title = ndb.StringProperty(required=False)
	description = ndb.TextProperty(indexed=True, required=True)
	members = ndb.StringProperty(repeated=True)
	folder = ndb.StringProperty()
	groupName = ndb.StringProperty()

	@classmethod
	def getFromId(cls, id):
		return cls.get_by_id(long(id))

class ProjectSnippet(ndb.Model):
	"""NDB model for a project weekly snippet.
	"""
	content = ndb.TextProperty()