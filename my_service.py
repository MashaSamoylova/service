# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import sqlite3
import random
import os

users_db = sqlite3.connect('users.db')
cur = users_db.cursor()

fake_db = sqlite3.connect('fake.db')
fake_cur = fake_db.cursor()


#cur.execute('''CREATE TABLE users(id INTEGER PRIMARY KEY, login VARCHAR(100),
#password VARCHAR(100), age INTEGER, capacity VARCHAR(100), secret VARCHAR(100), avatar VARCHAR(100))''')
#users_db.commit()


#show all requests
import tornado.options
tornado.options.parse_command_line()


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.render("./templates/main_page.html")
            return
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)

class LoginHandler(BaseHandler):
    def get(self):
        self.render("./templates/main2.html")

    def post(self):
        pretend_login = self.get_body_argument('login').decode('base64')
        pretend_password = self.get_body_argument('password').decode('base64')
        print pretend_login
        cur = users_db.cursor()
        print '''SELECT * FROM users WHERE login=%s AND password=%s''' %(pretend_login, pretend_password)
        try:
            cur.execute('''SELECT * FROM users WHERE login="%s" AND password="%s"''' %(pretend_login,pretend_password))
            for row in cur:
                print row
                self.set_secure_cookie("user", row[1])
                self.redirect("/myprofile")
                return
            self.redirect("/login")
        except:
            self.redirect("/login")

class RegistrationHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("./templates/registration.html", msg="")

    def post(self):
        print self.get_body_argument('login')
        cur = users_db.cursor()
        cur.execute('''SELECT COUNT(*) FROM users WHERE login=?''', (self.get_body_argument('login'),))
        for row in cur:
            if row[0]:
                self.render("./templates/registration.html", msg = "This login is busy")
        try:
            int_age = int(self.get_body_argument('age'))
        except:
            self.render("./templates/registration.html", msg = "Age should be numeric")
            return
        cur = users_db.cursor()
        cur.execute('''INSERT INTO users (id, login, password, age, capacity, secret, avatar)
                    VALUES(NULL,?,?,?,?,?, "./static/images/mprofile.png")''',
                    (self.get_body_argument('login'),
                    self.get_body_argument('password'),
                    int_age,
                    self.get_body_argument('capacity'),
                    self.get_body_argument('secret_place')))
        self.set_secure_cookie("user", self.get_body_argument('login'))
        users_db.commit()
        self.redirect('/myprofile')

class MyprofileHandler(BaseHandler):
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        print name
        cur = users_db.cursor()
        cur.execute('''SELECT * FROM users WHERE login=?''', (name,))
        for row in cur:
            print tornado.escape.utf8(row[4])
           # self.set_header('Content-Type', 'text/text; charset="utf-8"')
            self.render("./templates/template_user_page.html",
                        title=name,
                        login=name,
                        age=row[3],
                        capacity=tornado.escape.to_unicode(row[4]),
                        secret_place=row[5],
                        photo=row[6])

class HlebHandler(BaseHandler):
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        fake_cur = fake_db.cursor()
        fake_cur.execute('''SELECT * FROM users WHERE login=?''', (name,))
        for row in fake_cur:
            self.render("./templates/template_user_page.html",
                        title=name,
                        login=name,
                        age=row[3],
                        capacity=row[4],
                        secret_place=row[5],
                        photo=row[6])

class PhotoHandler(BaseHandler):
    def post(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        print name
        photo = self.request.files['photo'][0]['body']
        name_photo = self.request.files['photo'][0]['filename']
        with open("./static/images/photo_users/" + name_photo + ".jpg", 'w') as f:
            f.write(photo)
            f.close()
            cur = users_db.cursor()
            cur.execute('''UPDATE users SET avatar=? WHERE login=?''', ("./static/images/photo_users/" + name_photo + ".jpg", name))
            users_db.commit()
            self.redirect('/myprofile')

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect('/')

class HlebushekHandler(BaseHandler):
    def get(self):
        self.render("./templates/template_user_page.html",
                    title="hlebushek",
                    login="hlebushek",
                    age=112,
                    capacity="u tebya ne poluchitsy",
                    secret_place="sqlmap",
                    photo="./static/images/mprofile.png")

class CapHandler(BaseHandler):
    def post(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        cur = users_db.cursor()
        cur.execute('''UPDATE users SET capacity=? WHERE login=?''', (self.get_body_argument('cap'), name))
        users_db.commit()
        self.redirect('/myprofile')

class FakeHandler(BaseHandler):
    def post(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.set_header('Content-Type', 'text/text; charset="utf-8"')
        self.render("./templates/fake.html",
                    title="Hlebushek",
                    name="sdfsdfsdfsdf"+name[0]+"fhddfghdfhgh",
                    capacity=self.get_body_argument('fake')
        )




settings = {
    "templates_path": os.path.join(os.path.dirname("./templates"), "templates"),
    "static_path": os.path.join(os.path.dirname("./static"), "static"),
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
}

def make_app():
    return tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/registration", RegistrationHandler),
    (r"/myprofile", MyprofileHandler),
    (r"/hleb", HlebHandler),
    (r"/photo", PhotoHandler),
    (r"/logout", LogoutHandler),
    (r"/changecapacity", CapHandler),
    (r"/fn", FakeHandler),
    ], **settings)

if __name__=="__main__":
    app = make_app()
    app.listen(8888)
    print "Service started!\n"
    tornado.ioloop.IOLoop.current().start()
    print addslahes("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'")
