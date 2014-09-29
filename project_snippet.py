from google.appengine.api import users
from google.appengine.ext import ndb
from datetime import datetime
from datetime import timedelta

import os
import logging
import jinja2
import webapp2
from model import ProjectSnippet

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

class ProjectSnippetHandler(webapp2.RequestHandler):
	SNIPPET_START_DATE = datetime(2014, 1, 6) # First Mon of 2014 

	@staticmethod
	def weekRange(week):
		"""For a given week, returns the start and end date as human friendly strings.
		   e.g. 29 => `23, Jul 2014 (Wednesday) and 29, Jul 2014 (Tuesday)`
		"""
		start_date = ProjectSnippetHandler.SNIPPET_START_DATE + timedelta(days=7*week)
		end_date   = ProjectSnippetHandler.SNIPPET_START_DATE + timedelta(days=7*(week+1)-1)
		return {"start": "{:%d, %b %Y (%a)}".format(start_date),
				"end": "{:%d, %b %Y (%a)}".format(end_date) }

	def get(self, projectId, _week=None):
		current_week = (datetime.today() - ProjectSnippetHandler.SNIPPET_START_DATE).days / 7
		isEmbed = self.request.get("embedded", default_value="false")

		"""We handle various default options using redirect.
		   - default user = logged in user.
		   - default week = this week.
		"""
	
		if _week == None:
			self.redirect('/project-snippet/%s/%d?embedded=%s' % (projectId, current_week, isEmbed))
			return

		week = int(_week)
		
		edit = True
		
		# We get the snippet from the database if any.
		projectSnippet = ProjectSnippet.get_by_id(parent=ndb.Key("Project", projectId), id=week)
		if projectSnippet:
			snippet_data = projectSnippet.content
		else:
			snippet_data = "N/A"

		template = JINJA_ENVIRONMENT.get_template('templates/project_snippet.html')
		template_values = {
			'project': projectSnippet,
			'projectId': projectId,
			'start_date': ProjectSnippetHandler.weekRange(week)['start'],
			'end_date': ProjectSnippetHandler.weekRange(week)['end'],
			'snippet_content': snippet_data,
			'week': week,
			'prev_week': week-1,
			'next_week': week+1,
			'edit': edit,
			'embedded': isEmbed
		}
		self.response.out.write(template.render(template_values))

	def post(self, projectId, week):
		isEmbed = self.request.get("embedded", default_value="false")
		snippet_data = self.request.get('snippet_data')
		snippet = ProjectSnippet(parent=ndb.Key("Project", projectId), id=int(week), content=snippet_data)
		snippet.put()
		self.redirect('/project-snippet/%s/%s?embedded=%s' % (projectId, week, isEmbed))

app = webapp2.WSGIApplication([
	(r'/project-snippet/(.+)/(.+)', ProjectSnippetHandler),
	(r'/project-snippet/(.+)', ProjectSnippetHandler),
	], debug=True)
