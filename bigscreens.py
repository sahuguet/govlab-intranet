#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import logging

import webapp2
import jinja2
import json
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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def getCalendarService():
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
		scope=['https://www.googleapis.com/auth/calendar.readonly'],
		sub=USER_DELEGATION)
	http = httplib2.Http()
	http = credentials.authorize(http)
	service = build(serviceName='calendar', version='v3', http=http)
	return service

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
	service = getCalendarService()
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

class BigScreensHandler(webapp2.RequestHandler):
	def get(self):
		ip = self.request.remote_addr
# IP filtering
#		if not(os.environ['SERVER_SOFTWARE'].startswith('Development')) and ('.'.join(ip.split('.')[0:2]) not in ['216.165', '128.238']):
#			self.abort(403)

		template = JINJA_ENVIRONMENT.get_template('templates/bigscreens.html')
		events = getEventsForToday()
		logging.info(events)
		template_data = { 'events': events, 'day': 'Today' }
		self.response.out.write(template.render(template_data))

app = webapp2.WSGIApplication([
	('/bigscreens', BigScreensHandler),
], debug=True)