import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import logging
import httplib2
from apiclient.discovery import build
from oauth2client import client
from apiclient import discovery
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets
import webapp2
from google.appengine.api import users
from google.appengine.api import memcache

from model import UserProfile

decorator = OAuth2DecoratorFromClientSecrets(
	os.path.join(os.path.dirname(__file__), '__SECRETS__/client_secrets.json'),
	['https://www.googleapis.com/auth/plus.me'])

class GooglePlusHandler(webapp2.RequestHandler):
	@decorator.oauth_aware
	def get(self):
		user = users.get_current_user()
		me = user.email()
		if decorator.has_credentials():
			service = build('plus', 'v1')
			result = service.people().get(userId='me').execute(http=decorator.http())
			photoUrl = result['image']['url']
			user_profile = UserProfile.getFromGAE(user)
			user_profile.photoUrl = photoUrl
			user_profile.put()
			self.redirect('/profile')
		else:
			logging.info('no credentials')
			url = decorator.authorize_url()
			logging.info(url)
			self.redirect(url)

app = webapp2.WSGIApplication([
    ('/googleplus', GooglePlusHandler),
    (decorator.callback_path, decorator.callback_handler()),
], debug=True)
