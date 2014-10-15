import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import webapp2
import logging
from linkedin_auth import LinkedinAPI
from webapp2_extras import sessions
import json

from domain_services import getMyProfile

class BaseHandler(webapp2.RequestHandler):
	def dispatch(self):
  # Get a session store for this request.
		self.session_store = sessions.get_store(request=self.request)
		try:
    # Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
		finally:
		# Save all sessions.
			self.session_store.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
	# Returns a session using the default cookie key.
		return self.session_store.get_session()

API_KEY = '77e7muxgja1tnp'
API_SECRET = '8fg9mGdNuvIIMrtn'
CALLBACK = 'http://intranet.thegovlab.org/linkedin-callback' # 'http://localhost:16080/linkedin-callback

class LinkedInHandler(BaseHandler):
	def get(self):
		l = LinkedinAPI(api_key=API_KEY,
    api_secret=API_SECRET,	
    callback_url=CALLBACK,
    permissions=["r_fullprofile"])

		auth_props = l.get_authentication_tokens()
		auth_url = auth_props['auth_url']

		#Store this token in a session or something for later use in the next step.
		oauth_token_secret = auth_props['oauth_token_secret']
		self.session['linkedin_session_keys'] = {}
		self.session['linkedin_session_keys']['oauth_token_secret'] = oauth_token_secret
		logging.info(auth_url)
		self.redirect(auth_url)

class LinkedInCallbackHandler(BaseHandler):
	def get(self):
		me = getMyProfile()
		oauth_token = self.request.get('oauth_token')
		oauth_verifier = self.request.get('oauth_verifier')

		l = LinkedinAPI(api_key=API_KEY,
		api_secret=API_SECRET,
		oauth_token=oauth_token,
		oauth_token_secret=self.session['linkedin_session_keys']['oauth_token_secret'])

		authorized_tokens = l.get_access_token(oauth_verifier)
		logging.info(authorized_tokens)
		final_oauth_token = authorized_tokens['oauth_token']
		final_oauth_token_secret = authorized_tokens['oauth_token_secret']

		data = { '1': final_oauth_token_secret, '2': final_oauth_token}

		l = LinkedinAPI(api_key = API_KEY,
              api_secret = API_SECRET,
              oauth_token=final_oauth_token,
              oauth_token_secret=final_oauth_token_secret)

# list of fields to choose from: https://developer.linkedin.com/documents/profile-fields
		linkedinProfile = l.get('people/~', fields='first-name,last-name,picture-url,industry,summary,positions,educations,skills,interests,languages')

		me.linkedin = { 'oauth_token': final_oauth_token,
		'oauth_token_secret': final_oauth_token_secret,
		'profile': linkedinProfile}
		me.put()
		self.response.write("<h1>LinkedIn profile retrieved successfully.</h1><pre>%s</pre>" % json.dumps(linkedinProfile, indent=2))

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'REsfHxAVTTRmDwRetFgV',
}

app = webapp2.WSGIApplication([
  ('/linkedin', LinkedInHandler),
  ('/linkedin-callback', LinkedInCallbackHandler),
], debug=True, config=config)