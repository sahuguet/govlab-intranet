import jinja2
import json
import logging
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# We define a bunch of filters to make the templates simpler and catch bad data.
JINJA_ENVIRONMENT.filters['getProfile'] = lambda x: getUsersMapping().setdefault(x, x)
JINJA_ENVIRONMENT.filters['defaultName'] = lambda x: "%s %s" % (x.fname, x.lname) if x.fname and x.lname else x.email
JINJA_ENVIRONMENT.filters['fullName'] = lambda x: "%s %s" % (x.fname, x.lname) if type(x) is UserProfile else x
JINJA_ENVIRONMENT.filters['affiliation'] = lambda x: "%s" % x.affiliation if type(x) is UserProfile else 'N/A'
JINJA_ENVIRONMENT.filters['photoUrl'] = lambda x: x.photoUrl
JINJA_ENVIRONMENT.filters['defaultPicture'] = lambda x: x if x or x!=None else '/assets/silhouette200.png'
JINJA_ENVIRONMENT.filters['primaryEmail'] = lambda x: x.key.id()
JINJA_ENVIRONMENT.filters['projectId'] = lambda x: x.key.id()
JINJA_ENVIRONMENT.filters['projectTitle'] = lambda x: x.title if x.title != '' else "Untitled project"
JINJA_ENVIRONMENT.filters['asList'] = lambda x: ", ".join(x)

from google.appengine.api import users
from model import UserProfile
def getMyProfile():
	user = users.get_current_user()
	me = UserProfile.getFromGAE(user)
	return me

get_template = lambda x: ( { 'myself': getMyProfile(),
'logout_url': users.create_logout_url('/'),
'login_url': users.create_login_url('/') }, JINJA_ENVIRONMENT.get_template(x))

DOMAIN_ADMINS = [ 'arnaud@thegovlab.org ']

def canEditThisProfile(userProfile):
	return users.is_current_user_admin() or (users.get_current_user().email() in DOMAIN_ADMINS) or (userProfile.email == users.get_current_user().email())

def createNewUser(fname, lname, email):
	newUser = UserProfile.getFromEmail(email)
	if newUser == None:
		newUser = UserProfile(id=email, fname=fname, lname=lname, email=email)
		newUser.put()
		logging.info('User %s created.' % email)
	else:
		logging.error('User already exists.')