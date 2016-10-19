#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import jinja2
import webapp2
from google.appengine.ext import ndb


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")

    def post(self):
        user = self.request.get("name")
        mail = self.request.get("email")
        note = self.request.get("book")
        von = self.request.get("begin")
        bis = self.request.get("end")

        msg = Message(user_name = user, mail_adress = mail, user_start = von, user_end = bis, message_text = note)
        msg.put()
        self.write("Vielen Dank für Ihren Eintrag")
        self.render_template("hello.html")


class Message(ndb.Model):
    user_name = ndb.StringProperty()
    mail_adress = ndb.StringProperty()
    message_text = ndb.StringProperty()
    user_start = ndb.StringProperty()
    user_end = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)


class BookListHandler(BaseHandler):
    def get(self):
        messages = Message.query().fetch()
        params = {"messages": messages}
        return self.render_template("book_entry.html", params=params)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/book-entry', BookListHandler),
], debug=True)
