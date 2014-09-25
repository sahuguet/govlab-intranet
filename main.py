#!/usr/bin/env python
import os
import logging

import webapp2
import jinja2
import json

from google.appengine.api import users
from google.appengine.api import memcache

from model import UserProfile, Project
from domain_services import get_template
from domain_services import getMyProfile
from domain_services import canEditThisProfile

class MainHandler(webapp2.RequestHandler):
	def get(self):
		(template_data, template) = get_template('templates/main.html')
		template_data['test'] = 'test'
		logging.info(template_data)
		self.response.out.write(template.render(template_data))

class TeamHandler(webapp2.RequestHandler):
	def get(self):
		govlabUsers = UserProfile.query().order(UserProfile.lname, UserProfile.fname).fetch(limit=50)
		(template_data, template) = get_template('templates/team.html')
		template_data['team'] = govlabUsers 
		self.response.out.write(template.render(template_data))

class ProfileHandler(webapp2.RequestHandler):
	def get(self):
		if self.request.get('user_email'):
			userProfile = UserProfile.getFromEmail(self.request.get('user_email'))
		else:
			userProfile = getMyProfile()
		(template_data, template) = get_template('templates/profile.html')
		userProfileData = {}
		profile_data = json.loads(userProfile.profile) if userProfile.profile else {}
		for field in UserProfile.getJsonFields():
			userProfileData[field] = profile_data.setdefault(field, '')
		template_data['user'] = userProfile
		template_data['user_profile'] = userProfileData
		template_data['profileId'] = userProfile.email
		template_data['readonly'] = not(canEditThisProfile(userProfile))
		self.response.out.write(template.render(template_data))

	def post(self):
		user = users.get_current_user()
		profileId = self.request.get('profileId')
		logging.info('Fetching profile for %s' % profileId)
		userProfile = UserProfile.getFromEmail(profileId)
		logging.info(userProfile)
		if userProfile is None or canEditThisProfile == False:
			self.abort(404)
		user_profile_json = {}
		for field in UserProfile.getJsonFields():
			user_profile_json[field] = self.request.get(field)
		userProfile.profile = json.dumps(user_profile_json)
		userProfile.put()
		logging.info('profile stored')
		self.redirect('/profile?%s' % profileId)

class AllProjectsHandler(webapp2.RequestHandler):
	def get(self):
		(template_data, template) = get_template('templates/all_projects.html')
		all_projects = Project.query().order(Project.title).fetch()
		template_data['projects'] = all_projects
		self.response.out.write(template.render(template_data))

class ProjectHandler(webapp2.RequestHandler):
	def get(self, projectId):
		project = Project.getFromId(projectId)
		(template_data, template) = get_template('templates/project.html')
		template_data['project'] = project
		self.response.out.write(template.render(template_data))

	def post(self, projectId):
		project = Project.getFromId(projectId)
		project.title = self.request.get('title')
		project.description = self.request.get('description')
		project.members = map(lambda x:x.strip(), self.request.get('members').split(','))
		project.folder = self.request.get('folder')
		project.put()
		self.redirect('/project/%s' % projectId)

class NewProjectHandler(webapp2.RequestHandler):
	def get(self):
		(template_data, template) = get_template('templates/project.html')
		template_data['project'] = {}
		self.response.out.write(template.render(template_data))

	def post(self):
		project = Project(title=self.request.get('title'),
			description=self.request.get('description'),
			members=map(lambda x:x.strip(), self.request.get('members').split(',')))
		project.put()
		self.redirect('/project/%s' % project.key.id())

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/team', TeamHandler),
	('/profile', ProfileHandler),
	('/project/all', AllProjectsHandler),
	(r'/project/(\d+)$', ProjectHandler),
	('/project/new', NewProjectHandler),
], debug=True)