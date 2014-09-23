#!/usr/bin/env python
import os
import logging

import webapp2
import jinja2

from google.appengine.api import users
from google.appengine.api import memcache

from domain_services import *

class MainHandler(webapp2.RequestHandler):
	def get(self):
		logging.info(self.request.referer)
		user = users.get_current_user()
		template = get_template('templates/main.html')
		template_values = {}
		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
	('/', MainHandler),
], debug=True)