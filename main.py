#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import jinja2
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users



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
        hommesse = Message.query(Message.deleted == False).fetch()
        user = users.get_current_user()
        logged_in = user is not None

        params = {"hommesse": hommesse, "user": user, "logged_in": logged_in}

        if logged_in:
            params["logout_url"] = users.create_logout_url('/')
        else:
            params["login_url"] =  users.create_login_url('/')
            
        return self.render_template("hello.html", params=params)

    def post(self):
        user = self.request.get("name")
        mail = self.request.get("email")
        note = self.request.get("book")
        von = self.request.get("begin")
        bis = self.request.get("end")

        msg = Message(user_name = user, mail_adress = mail, user_start = von, user_end = bis, message_text = note)
        msg.put()
        self.write("Vielen Dank für Ihren Eintrag")
        hommesse = Message.query().fetch()
        params = {"hommesse": hommesse}
        return self.render_template("hello.html", params=params)


class Message(ndb.Model):
    user_name = ndb.StringProperty()
    mail_adress = ndb.StringProperty()
    message_text = ndb.StringProperty()
    user_start = ndb.StringProperty()
    user_end = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)

class BookListHandler(BaseHandler):
    def get(self):
        messages = Message.query().fetch()
        params = {"messages": messages}
        return self.render_template("book_entry.html", params=params)

class EditMessageHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("message_edit.html", params=params)

    def post(self, message_id):
        new_text = self.request.get("some_text")
        message = Message.get_by_id(int(message_id))
        message.message_text = new_text
        message.put()
        return self.redirect_to("msg-list")

class DeleteMessageHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("message_delete.html", params=params)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        message.deleted = True
        message.put()
        return self.redirect_to("msg-list")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/book-entry', BookListHandler, name="msg-list"),
    webapp2.Route('/message/<message_id:\d+>/edit', EditMessageHandler),
    webapp2.Route('/message/<message_id:\d+>/delete', DeleteMessageHandler),
], debug=True)
