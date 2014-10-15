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
  SNIPPET_START_DATE = datetime(2014, 1, 6) # First Mon of 2014 

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
      self.redirect('/snippet/%s/%d?embedded=%s' % (_userEmail, current_week - 1, isEmbed))
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
  def get(self, _week=None):
    current_week = ((datetime.today() - SnippetHandler.SNIPPET_START_DATE).days / 7) - 1
    if _week:
      current_week = int(_week)
    # We get all the snipptet for the week before.
    # 
    snippets = []
    for s in sorted(UserSnippet.getAllSnippetsByWeek(current_week), key=lambda x: x.key.id()):
      snippets.append((s.key.id(), s.content))
    (template_data, template) = get_template('templates/all_snippets.html')
    template_data['snippets'] = snippets
    template_data['prev_week'] = current_week -1
    template_data['next_week'] = current_week +1
    template_data['start_date'] = SnippetHandler.weekRange(current_week)['start']
    template_data['end_date'] = SnippetHandler.weekRange(current_week)['end']
    self.response.out.write(template.render(template_data))

class MainHandler(webapp2.RequestHandler):
  def get(self):
    self.response.write("default route")

# Support for email
from email.utils import parseaddr
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import mail
class SnippetEmailHandler(InboundMailHandler):
  def receive(self, mail_message):
    week = ((datetime.today() - SnippetHandler.SNIPPET_START_DATE).days / 7) - 1
    (name, userEmail) = parseaddr(mail_message.sender)
    logging.info(userEmail)
    logging.info(mail_message.bodies('text/plain'))
    body = [body for (content_type, body) in mail_message.bodies('text/plain')][0]
    logging.info(body)
    subject = mail_message.subject if hasattr(mail_message, 'subject') else 'Missing subject field'
    snippet_data = body.decode()
    snippet = UserSnippet.getSnippet(userEmail, week)
    if snippet:
      snippet.content = snippet.content + "\n" + snippet_data
      logging.info('Snippet updated;\nadding content %s' % snippet_data)
    else:
      snippet = UserSnippet.createSnippet(userEmail, week, snippet_data)
      logging.info('New snippet created with content:\n%s' % snippet_data)
    snippet.put()
    message = mail.EmailMessage()
    message.sender = "snippets@govlab-intranet.appspotmail.com"
    message.to = userEmail
    message.body = """Your snippet has been updated.
    
    You can edit your snippet at http://intranet.thegovlab.org/snippet/.

    The snippet master.
    """
    message.send()
    logging.info('Snippet created/updated + reply sent to user.')

app = webapp2.WSGIApplication([
  (r'/snippet/all$', AllUserSnippetsHandler),
  (r'/snippet/all/(\d+)$', AllUserSnippetsHandler),
  (r'/snippet/(.+)/(.+)', SnippetHandler),
  (r'/snippet/(.+)', SnippetHandler),
  (r'/snippet/', SnippetHandler),
  (SnippetEmailHandler.mapping()),
  ], debug=True)