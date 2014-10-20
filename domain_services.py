import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import jinja2
import json
import logging
import markdown2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

MD = markdown2.Markdown()

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
JINJA_ENVIRONMENT.filters['markdown'] = lambda x: MD.convert(x)

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

def getDomainUsers():
	import httplib2
	from apiclient.discovery import build
	from oauth2client.client import SignedJwtAssertionCredentials
	SERVICE_ACCOUNT_EMAIL = '185449059606-fevoglds8eifup46cn6p6aph7vg5oihj@developer.gserviceaccount.com'
	if os.environ['SERVER_SOFTWARE'].startswith('Development'):
		SERVICE_ACCOUNT_PKCS12_FILE_PATH = '__SECRETS__/govlab-intranet.p12'
	else:
		SERVICE_ACCOUNT_PKCS12_FILE_PATH = '__SECRETS__/govlab-intranet.pem'
	USER_DELEGATION = 'arnaud@thegovlab.org'
	f = file(SERVICE_ACCOUNT_PKCS12_FILE_PATH, 'rb')
	key = f.read()
	f.close()
	credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL,
		key,
		scope=['https://www.googleapis.com/auth/admin.directory.user'],
		sub=USER_DELEGATION)
	http = httplib2.Http()
	http = credentials.authorize(http)
	service = build('admin', 'directory_v1', http=http)
	return service.users().list(domain='thegovlab.org', maxResults=500, orderBy='familyName').execute()['users']