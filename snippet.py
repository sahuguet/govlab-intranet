from google.appengine.api import users
from google.appengine.ext import ndb
from datetime import datetime
from datetime import timedelta

import os
import logging
import jinja2
import webapp2
from model import UserSnippet
from domain_services import get_template

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class SnippetHandler(webapp2.RequestHandler):
  SNIPPET_START_DATE = datetime(2014, 1, 1) # First Wed of 2014 

  @staticmethod
  def weekRange(week):
    """For a given week, returns the start and end date as human friendly strings.
    e.g. 29 => `23, Jul 2014 (Wednesday) and 29, Jul 2014 (Tuesday)`
    """
    start_date = SnippetHandler.SNIPPET_START_DATE + timedelta(days=7*week)
    end_date   = SnippetHandler.SNIPPET_START_DATE + timedelta(days=7*(week+1)-1)
    return {"start": "{:%d, %b %Y (%a)}".format(start_date),
      "end": "{:%d, %b %Y (%a)}".format(end_date) }

  def get(self, _userEmail=None, _week=None):
    myself = users.get_current_user()
    current_week = (datetime.today() - SnippetHandler.SNIPPET_START_DATE).days / 7
    isEmbed = self.request.get("embedded", default_value="false")

    """We handle various default options using redirect.
       - default user = logged in user.
     - default week = this week.
    """
    if _userEmail == None:
      self.redirect('/snippet/%s?embedded=%s' % (myself.email(), isEmbed))
      return
    if _week == None:
      self.redirect('/snippet/%s/%d?embedded=%s' % (_userEmail, current_week, isEmbed))
      return

    # Starting from here, both `_user` and `_week` are properly assigned.
    userEmail = _userEmail
    week = int(_week)
      
    edit = False
    if _userEmail == myself.email():
      edit = True
      
      # We get the snippet from the database if any.
    snippet = UserSnippet.getSnippet(userEmail, week)
    if snippet:
      snippet_data = snippet.content
    else:
      snippet_data = "N/A"

    template = JINJA_ENVIRONMENT.get_template('templates/snippet.html')
    template_values = {
      'userEmail': userEmail,
      'start_date': SnippetHandler.weekRange(week)['start'],
      'end_date': SnippetHandler.weekRange(week)['end'],
      'snippet_content': snippet_data,
      'week': week,
      'prev_week': week-1,
      'next_week': week+1,
      'edit': edit,
      'embedded': isEmbed
    }
    self.response.out.write(template.render(template_values))

  def post(self, userEmail, week):
    logging.info("Inside POST")
    myself = users.get_current_user()
    isEmbed = self.request.get("embedded", default_value="false")
    # Only a user can update her snippet.
    if userEmail != myself.email():
      self.abort(403)

    snippet_data = self.request.get('snippet_data')
    snippet = UserSnippet.createSnippet(userEmail, week, snippet_data)
    snippet.put()
    self.redirect('/snippet/%s/%s?embedded=%s' % (userEmail, week, isEmbed))

class AllUserSnippetsHandler(webapp2.RequestHandler):
  def get(self):
    current_week = (datetime.today() - SnippetHandler.SNIPPET_START_DATE).days / 7
    # We get all the snipptet for a given week.
    snippets = {}
    for s in UserSnippet.getAllSnippetsByWeek(current_week):
      snippets[s.key.id()] = s.content
    (template_data, template) = get_template('templates/all_snippets.html')
    template_data['snippets'] = snippets
    self.response.out.write(template.render(template_data))

class MainHandler(webapp2.RequestHandler):
  def get(self):
    self.response.write("default route")

app = webapp2.WSGIApplication([
  (r'/snippet/all', AllUserSnippetsHandler),
  (r'/snippet/(.+)/(.+)', SnippetHandler),
  (r'/snippet/(.+)', SnippetHandler),
  (r'/snippet/', SnippetHandler),
  ], debug=True)