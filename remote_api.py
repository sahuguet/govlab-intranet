import sys
import csv
import glob
import json
import re
sys.path.append('/usr/local/google_appengine')
for l in glob.glob("/usr/local/google_appengine/lib/*"):
	sys.path.append(l)

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import ndb
from google.appengine.api import mail

from model import UserProfile, Project
import getpass

def auth_func():
	password = 'ockbozzqkzeynkak'
  #return (raw_input('Username:'), getpass.getpass('Password:'))
	return ('arnaud@thegovlab.org', password)

remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func,
  'govlab-intranet.appspot.com'
  )

import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
SERVICE_ACCOUNT_EMAIL = '185449059606-fevoglds8eifup46cn6p6aph7vg5oihj@developer.gserviceaccount.com'
SERVICE_ACCOUNT_PKCS12_FILE_PATH = '__SECRETS__/govlab-intranet.p12'
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

#print service.users()
#for user in service.users().list(domain='thegovlab.org', maxResults=500).execute()['users']:
#	if user['orgUnitPath'] == '/':
#		print user

def createDomainUsers():
	from domain_services import createNewUser
	for user in service.users().list(domain='thegovlab.org', maxResults=500).execute()['users']:
		if user['orgUnitPath'] == '/':
			print user
			createNewUser(user['name']['givenName'], user['name']['familyName'], user['primaryEmail'])

def deleteAllDomainUsers(dryRun=True):
	if dryRun:
		retunr
	from model import UserProfile
	all_users_keys = UserProfile.query().fetch(keys_only=True)
	for key in all_users_keys:
		key.delete()

#deleteAllDomainUsers(dryRun=False)
#createDomainUsers()
#from google.appengine.api import users
#print users.User(email="arnaud@thegovlab.org").key

def addDomain(array):
	return map(lambda x:x+'@thegovlab.org', array)

def createRandomProjects():
	p = Project(title="GovLab Academy", description="bla bla", members=addDomain(['arnaud', 'nikki', 'luis']))
	p.put()
	p = Project(title="ICANN", description="bla bla", members=addDomain(['arnaud', 'antony', 'samantha']))
	p.put()
	p = Project(title="OrgPedia", description="bla bla", members=addDomain(['arnaud', 'miller']))
	p.put()

#print Project.get_by_id(long('5629499534213120'))
#from domain_services import createNewUser
#createNewUser('Lisbeth', 'Salander', 'lisbeth@thegovlab.org')
from model import ProjectSnippet, UserSnippet
#p = ProjectSnippet(parent=ndb.Key("Project", 124), id=int(45), content="")
#p.put()
#print dir(p.key)
#print p.key.parent().id()
#s = UserSnippet.createSnippet('arnaud3@thegovlab.org', 12, 'test')
#s.put()
#s = UserSnippet.createSnippet('arnaud2@thegovlab.org', 12, 'test')
#s.put()
#for i in [7,6,5,8]:
#	s = UserSnippet.createSnippet('arnaud%d@thegovlab.org' % i, 12, 'test')
#	s.put()
#for s in UserSnippet.getAllSnippetsByWeek(12):
#	print s.key.id()
all_users =  [k.id() for k in UserProfile.query().fetch(keys_only=True)]
users_with_snippets = [k.key.id() for k in UserSnippet.getAllSnippetsByWeek(38)]
print set(all_users) - set(users_with_snippets)
