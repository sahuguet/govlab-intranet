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

#remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func,
#  'govlab-intranet.appspot.com'
#  )

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
#	scope=['https://www.googleapis.com/auth/admin.directory.user'],
	scope=['https://www.googleapis.com/auth/calendar.readonly'],
	sub=USER_DELEGATION)
http = httplib2.Http()
http = credentials.authorize(http)
#service = build('admin', 'directory_v1', http=http)

service = build(serviceName='calendar', version='v3', http=http)

calendar = service.calendars().get(calendarId='big-screens@thegovlab.org').execute()
print calendar

from datetime import datetime
from datetime import timedelta


import pytz
today = datetime.now(pytz.timezone('US/Eastern'))
oneday = today + timedelta(days=1)
oneweek = today + timedelta(days=7)
onemonth = today + timedelta(days=30)

dateFormat = lambda x:x.strftime("%Y-%m-%dT%H:%M:%S%z")

PARAMS = { 'calendarId':'big-screens@thegovlab.org',
	'singleEvents':True,
	'timeMin': dateFormat(today),
	'orderBy':'startTime' }

def getEventsForToday():
	params = PARAMS.copy()
	params['timeMax'] = dateFormat(oneday)
	return getEvents(params)

def getEventsForNextWeek():
	params = PARAMS.copy()
	params['timeMax'] = dateFormat(oneweek)
	return getEvents(params)

def getEventsForNextMonth():
	params = PARAMS.copy()
	params['timeMax'] = dateFormat(onemonth)
	return getEvents(params)

def getEvents(query_params):
	params = query_params
	print params
	page_token = None
	all_events = []
	while True:
		if page_token:
			params['pageToken']=page_token
		events = service.events().list(**params).execute()
		for event in events['items']:
			all_events.append(event)
		page_token = events.get('nextPageToken')
		if not page_token:
			break
	return all_events

print "TODAY"
for event in getEventsForToday():
	print event['summary'], event['start'], event['end']

print "7days"
for event in getEventsForNextWeek():
	print event['summary'], event['start'], event['end']

print "30days"
for event in getEventsForNextMonth():
	print event['summary'], event['start'], event['end']

"""Scope for security setup:

http://www.googleapis.com/auth/admin.directory.user, https://www.googleapis.com/auth/admin.directory.user, https://www.googleapis.com/auth/calendar.readonly
"""


#print service.users()

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
#all_users =  [k.id() for k in UserProfile.query().fetch(keys_only=True)]
#users_with_snippets = [k.key.id() for k in UserSnippet.getAllSnippetsByWeek(38)]
#print set(all_users) - set(users_with_snippets)
#print UserProfile.get_by_id('arnaud@thegovlab.org').linkedin['profile']['summary']

def getUserLinkedinData():
	profiles = []
	for profile in UserProfile.query().fetch():
		if profile.linkedin: profiles.append(profile.linkedin['profile'])
	print json.dumps(profiles)

#getUserLinkedinData()

#for user in service.users().list(domain='thegovlab.org', maxResults=500).execute()['users']:
#	print user['primaryEmail']

"""
RANGE = range(36,42)
all_users = UserProfile.query().fetch()
snippet_stats = {}
for user in all_users:
	snippet_stats [user.key.id()] = {}
all_snippets = []
for i in RANGE:
	all_snippets.extend(UserSnippet.getAllSnippetsByWeek(i))
print "%d snippets found." % len(all_snippets)
for snippet in all_snippets:
	(week, user) = snippet.getWeekAndUser()
	snippet_stats.setdefault(user, {})[int(week)] = True
for user in sorted(snippet_stats.keys()):
	print user
	print [ snippet_stats[user].setdefault(k, False) for k in RANGE ]
"""

"""
all_users = []
for user in UserProfile.query().fetch():
	experience = 'N/A'
	if user.profile:
		experience = json.loads(user.profile)['experience']
	all_users.append({ 'fname': str(user.fname),
		'lname': str(user.lname),
		'email': str(user.email),
		'photoUrl': str(user.photoUrl),
		'experience': str(experience) })


import yaml
print yaml.dump(all_users, default_flow_style=False)
"""
"""
import yaml
all_projects = []
for project in Project.query().fetch():
	all_projects.append({ 'title': str(project.title),
		'description': project.description,
		'tags': map(lambda x:str(x), project.tags),
		'areas': map(lambda x:str(x), project.project_areas) })
print yaml.dump(all_projects, default_flow_style=False, allow_unicode=True)
"""

"""
from domain_services import getDomainUsers
currentUsers = [ k.id() for k in UserProfile.query().fetch(keys_only=True)]
domainUsers = [ k for k in getDomainUsers() if k['orgUnitPath'] == '/']
missingUsers = [k for k in domainUsers if k['primaryEmail'] not in currentUsers]
print len(missingUsers)
print [k['primaryEmail'] for k in missingUsers]
"""