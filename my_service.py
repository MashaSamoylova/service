# -*- coding: utf-8 -*-
import tornado.httpclient
import tornado.ioloop
import tornado.web
import sqlite3
import random
import shield
import json
import time
import os
from tornado import gen
from PIL import Image

port = 8888
db_file = './data_base.db'

#shows all requests
import tornado.options
tornado.options.parse_command_line()

def check_member(name):
    cur = db.cursor()
    cur.execute('''SELECT COUNT(*) FROM users WHERE login=?''', (name,))
    for row in cur:
        if row[0]:
            return 1
        else:
            return 0

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        name = self.get_secure_cookie('user')
        if check_member(name):
            self.redirect("/myprofile")
            return
        self.render("./templates/main_page.html")

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("./templates/main2.html")

    def post(self):
        pretend_login = shield.addslashes(self.get_body_argument('login'))
        pretend_password = self.get_body_argument('password')
        print pretend_login
        cur = db.cursor()
        try:
            cur.execute("SELECT * FROM users WHERE login='%s' AND password='%s'" %(pretend_login,pretend_password))
            for row in cur:
                print row
                self.set_secure_cookie("user", row[1])
                if row[1] == "admin":
                    self.set_secure_cookie("role", "juxeNj4cX8Nv") #!!!!!!!!!!!!!!!!!!!!!!!
                self.redirect("/myprofile")
                return
            self.redirect("/login")
        except:
            self.redirect("/login")

class RegistrationAskCodeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("./templates/ask_for_code.html", msg="")

    def post(self):
        code = self.get_body_argument('code')
        cur = db.cursor()
        try:
            cur.execute('''SELECT * FROM codes WHERE code=?''', (code,))
            for row in cur:
                self.render("./templates/registration.html", msg=row[2])
                return
            self.render("./templates/ask_for_code.html", msg="code is wrong")
        except:
            self.render("./templates/ask_for_code.html", msg="something is wrong")

class CheckUserHandler(tornado.web.RequestHandler):
    def post(self):
        if self.get_body_argument('name') == "OK!!!!":
            cur = db.cursor()
            cur.execute('''SELECT COUNT(*) FROM codes''')
            for row in cur:
                quantity = row[0]
            number = random.randint(0,quantity-1)
            cur.execute('''SELECT * FROM codes WHERE id=?''', (number,))
            for row in cur:
                print row[1]
                self.write(row[1])
        else:
            self.write("no")

class RegistrationHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("./templates/registration.html", msg="")

    def post(self):

        if not shield.clear_str(self.get_body_argument('login')):
            self.render("./templates/registration.html", msg = "Don't use the dangerous_symbols")
            return
        if not shield.clear_str(self.get_body_argument('password')):
            self.render("./templates/registration.html", msg = "Don't use the dangerous_symbols")
            return

        cur = db.cursor()
        cur.execute('''SELECT COUNT(*) FROM users WHERE login=?''', (self.get_body_argument('login'),))
        for row in cur:
            if row[0]:
                self.render("./templates/registration.html", msg = "This login is busy")
        try:
            int_age = int(self.get_body_argument('age'))
        except:
            self.render("./templates/registration.html", msg = "Age should be numeric")
            return
        cur = db.cursor()
        cur.execute('''INSERT INTO users (id, login, password, age, capacity, secret, avatar)
                    VALUES(NULL,?,?,?,?,?, "./static/images/mprofile.png")''',
                    (self.get_body_argument('login'),
                    self.get_body_argument('password'),
                    int_age,
                    self.get_body_argument('capacity'),
                    self.get_body_argument('secret_place')))
        self.set_secure_cookie("user", self.get_body_argument('login'))
        db.commit()
        self.redirect('/myprofile')

class MyprofileHandler(tornado.web.RequestHandler):
    def get(self):
        name = self.get_secure_cookie('user')
        if not check_member(name):
            self.redirect('/')
        cur = db.cursor()
        cur.execute('''SELECT * FROM users WHERE login=?''', (name,))
        for row in cur:
            self.render("./templates/template_user_page.html",
                        title=name,
                        login=name,
                        age=row[3],
                        capacity=tornado.escape.to_unicode(row[4]),
                        secret_place=row[5],
                        photo=row[6])

class PhotoHandler(tornado.web.RequestHandler):
    def post(self):
        name = self.get_secure_cookie('user')
        if not check_member(name):
            self.redirect('/')
        photo = self.request.files['photo'][0]['body']
        name_photo = self.request.files['photo'][0]['filename']
        with open("./static/images/photo_users/" + name_photo + ".jpg", 'w') as f:
            f.write(photo)
            f.close()
            cur = db.cursor()
            cur.execute(
                    '''UPDATE users SET avatar=? WHERE login=?''', 
                    ("./static/images/photo_users/" + name_photo + ".jpg", name)
                    )
            db.commit()
            self.redirect('/myprofile')

class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("role")
        self.redirect('/')

class MessageHandler(tornado.web.RequestHandler):
    def post(self):
        quantity = self.get_body_argument('lastMessage')
        cur = db.cursor()
        cur.execute('''SELECT COUNT(*) FROM news''')
        for row in cur:
            new_quantity = row[0]
        print quantity
        print new_quantity
        if new_quantity == int(quantity):
            print "is send 'no'"
            self.write("no")
            return
        cur = db.cursor()
        cur.execute('''SELECT * FROM news WHERE id>?''', (quantity,))
        messages = []
        for row in cur:
            messages.append(row[1])
        self.write(json.dumps(messages))

class NewsHandler(tornado.web.RequestHandler): #messages writes in dictionary 
    def get(self):
        name = self.get_secure_cookie('user')
        if not check_member(name):
            self.redirect('/')
        cur = db.cursor()
        cur.execute('''SELECT * FROM users WHERE login=?''', (name,))
        for row in cur:
            photo_user = row[6]
        cur = db.cursor()
        cur.execute('''SELECT COUNT(*) FROM news''')
        for row in cur:
            quantity = row[0]-10
        cur.execute('''SELECT * FROM news WHERE id=?''', (quantity,))
        for row in cur:
            num = row[0]
            msg = json.loads(row[1])
        try:    
            self.render("./templates/news.html",
                    photo = photo_user,
                    number = num,
                    img = 'data:image/png;base64,' + msg['photo'],
                    login = msg['login'],
                    text = msg['text']
                    )
        except:
            self.render("./templates/news.html",
                    photo = photo_user,
                    number = 0,
                    img = "",
                    login = "some login",
                    text = "some text"
                    )
    
    def post(self):
        name = self.get_secure_cookie('user')
        if name == None:
            self.redirect('/')
        message = self.get_body_argument('text')
        cur = db.cursor()
        cur.execute('''SELECT * FROM users WHERE login=?''', (name,))
        for row in cur:
            avatar = row[6]
        photo_bin = Image.open(row[6])
        resized_img = photo_bin.resize((64,64), Image.ANTIALIAS)
        resized_img.save("./small.jpeg")
        f = open("./small.jpeg")
        r = f.read().encode('base64')
        record = dict(login=name, text=message, time=time.ctime(), photo=r)
        cur  = db.cursor()
        cur.execute('''INSERT INTO news (id, message)
                        VALUES(NULL,?)''',
                        (json.dumps(record),))
        db.commit()

class WriteHandler(tornado.web.RequestHandler):
    def get(self):
        if self.get_secure_cookie("role") == "juxeNj4cX8Nv": #!!!!!!!!!!!!!!!!!
            self.render("./templates/write.html")
        else:
            self.write("Permission denied")

    def post(self):
        if self.get_secure_cookie("role") == "juxeNj4cX8Nv": #!!!!!!!!!!!!!!!!
            cur = db.cursor()
            cur.execute('''INSERT INTO codes (id, code,flag) VALUES(NULL,?,?)''', 
                    (
                        self.get_body_argument('code'),
                        self.get_body_argument('flag')
                    ))
            db.commit()
            self.redirect('/writecode')
        else:
            self.write("Permission denied")

settings = {
    "templates_path": os.path.join(os.path.dirname("./templates"), "templates"),
    "static_path": os.path.join(os.path.dirname("./static"), "static"),
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
}

def make_app():
    return tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/askcode", RegistrationAskCodeHandler),
    (r"/checkuser", CheckUserHandler),
    (r"/registration", RegistrationHandler),
    (r"/myprofile", MyprofileHandler),
    (r"/photo", PhotoHandler),
    (r"/logout", LogoutHandler),
    (r"/msg", MessageHandler),
    (r"/news", NewsHandler),
    (r"/writecode", WriteHandler),
    ], **settings)

if __name__=="__main__":
    db = sqlite3.connect(db_file)
    cur = db.cursor()
    cmd = '''
        CREATE TABLE IF NOT EXISTS
            users(
                id INTEGER PRIMARY KEY, 
                login VARCHAR(100),
                password VARCHAR(100), 
                age INTEGER, 
                capacity VARCHAR(100), 
                secret VARCHAR(100), 
                avatar VARCHAR(100)
            )'''
    cur.execute(cmd)
    db.commit()
    
    cmd = '''
        CREATE TABLE IF NOT EXISTS
            codes(
                id INTEGER PRIMARY KEY, 
                code VARCHAR(12), 
                flag VARCHAR(16)
        )'''
    cur.execute(cmd)
    db.commit()

    cmd = '''
        CREATE TABLE IF NOT EXISTS
            news(
                id INTEGER PRIMARY KEY, 
                message VARCHAR(100)
        )'''
    cur.execute(cmd)
    db.commit()

    app = make_app()
    app.listen(port)
    print "Service started!\nport: " + str(port)
    tornado.ioloop.IOLoop.current().start()
