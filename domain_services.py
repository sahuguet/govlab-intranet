import jinja2
import json
import logging
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# We define a bunch of filters to make the templates simpler and catch bad data.
JINJA_ENVIRONMENT.filters['getProfile'] = lambda x: getUsersMapping().setdefault(x, x)
JINJA_ENVIRONMENT.filters['fullName'] = lambda x: "%s %s" % (x.fname, x.lname) if type(x) is UserProfile else x
JINJA_ENVIRONMENT.filters['affiliation'] = lambda x: "%s" % x.affiliation if type(x) is UserProfile else 'N/A'
JINJA_ENVIRONMENT.filters['photoUrl'] = lambda x: x.photoUrl
JINJA_ENVIRONMENT.filters['defaultPicture'] = lambda x: x if x or x!=None else '/assets/silhouette200.png'
JINJA_ENVIRONMENT.filters['primaryEmail'] = lambda x: x.key.id()
JINJA_ENVIRONMENT.filters['projectId'] = lambda x: x.key.id()
JINJA_ENVIRONMENT.filters['projectTitle'] = lambda x: x.title if x.title != '' else "Untitled project"

get_template = JINJA_ENVIRONMENT.get_template