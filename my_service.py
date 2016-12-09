import tornado.ioloop
import tornado.web
import sqlite3
import os

users_db = sqlite3.connect('users.db')
cur = users_db.cursor()
#cur.execute('''CREATE TABLE users(id INTEGER PRIMARY KEY, login VARCHAR(100),
#password VARCHAR(100), secret VARCHAR(100), avatar VARCHAR(100))''')
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
        cur.execute('''SELECT * FROM users WHERE login=?''', (self.get_body_argument('login'),))
        for row in cur:
            if row[2] == self.get_body_argument('password'):
                self.set_secure_cookie("user", self.get_body_argument("login"))
                self.redirect('/myprofile')
        self.write("net")

class RegistrationHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("./templates/registration.html")

    def post(self):
        print self.get_body_argument('login')
    #    cur.execute() DJNNNJNHVHGKJKLHJFGDHHGJKL:"LKJHGFDGHJKL:"LKJHGFD
        cur.execute('''INSERT INTO users (id, login, password, secret, avatar) VALUES(NULL,?,?,?, "./static/images/mprofile.png")''',
        (self.get_body_argument('login'), self.get_body_argument('password'), self.get_body_argument('secret_place')))
        users_db.commit()
        self.redirect('/login')

class MyprofileHandler(BaseHandler):
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        cur.execute('''SELECT * FROM users WHERE login=?''', (name,))
        for row in cur:
            self.render("./templates/template_user_page.html", title=name, photo=row[4])

class PhotoHandler(BaseHandler):
    def post(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        photo = self.request.files['photo'][0]['body']
        with open("./static/images/photo_users" + name + ".jpg", 'w') as f:
            f.write(photo)
            f.close()
            cur.execute('''UPDATE users SET avatar=? WHERE login=?''', ("./static/images/photo_users/" + name + ".jpg", name))
            users_db.commit()
            self.redirect('/myprofile')

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect('/')


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
    (r"/photo", PhotoHandler),
    (r"/logout", LogoutHandler),
#    (r"/login", LogHandler),
    ], **settings)

if __name__=="__main__":
    app = make_app()
    app.listen(8888)
    print "Service started!\n"
    tornado.ioloop.IOLoop.current().start()
