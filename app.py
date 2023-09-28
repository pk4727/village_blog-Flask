from flask import Flask ,render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask_mail import Mail
import json
import math
import os

with open('D:\\code\\web_devlopment\\Flask\\flask1\\config.json','r') as config:
    parameters = json.load(config)["parameters"]

local_server = True
app = Flask(__name__)     

app.secret_key = 'secret_key-for-dashboard-login'
app.config['upload_folder'] = parameters['file_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT='456',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = "webworkingformail@gmail.com",
    MAIL_PASSWORD = "ufpupbjrpjumkpgi"
)
mail = Mail(app)

#configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = parameters['production_uri']

#initializing sqlalchemy
db = SQLAlchemy(app)

# all class which is used for puting database in server or call data by server :- ------------

class Blog_post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), nullable=False)
    content = db.Column(db.String(1000000), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)

class admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class contects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=False, nullable=False)
    phone_no = db.Column(db.String(100), unique=False, nullable=False)
    message = db.Column(db.Integer, unique=False, nullable=False)
    date = db.Column(db.String(20), unique=False, nullable=True)

# -----------------------------------------------------------------------------------------

@app.route("/post/<string:blog_post_slug>", methods=['GET'])
def Blog(blog_post_slug):
    post = Blog_post.query.filter_by(slug = blog_post_slug).first()
    return render_template("post.html", parameters = parameters, post = post)

# -----------------------------------------------------------------------------------------

@app.route("/")     
def home():
    # posts1= Blog_post.query.filter_by().all()[0:parameters['no_of_posts']]
    posts = Blog_post.query.filter_by().all()
    last = math.ceil(len(posts)/int(parameters['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[ (page-1)*int(parameters['no_of_posts']) : (page-1)*int(parameters['no_of_posts']) + int(parameters['no_of_posts']) ]
    if (page==1):
        previous = "#"
        next = "/?page="+str(page+1)
    elif(page==last):
        previous = "/?page="+str(page-1)
        next = "#"
    else:
       previous = "/?page="+str(page-1)
       next = "/?page="+str(page+1)
    return render_template("index.html", parameters = parameters, posts = posts, previous=previous, next=next)

# --------------------------------------------------------------------------------------

@app.route("/about")
def about():
    return render_template("about.html", parameters = parameters)
        
# ---------------------------------------------------------------------------------------

@app.route("/deshboard_login", methods=['GET','POST'])
def deshboard_login():
    username = request.form.get('user')
    password = request.form.get('password')
    post = admin.query.filter_by(username = username).first()
    datee = date.today()
    
    if 'user' in session:
        print("Already login into the page !")
        post = Blog_post.query.filter_by().all()
        return render_template("deshboard_data.html" ,posts = post)
    
    elif post==None:                                                  # if any error in login details
        # message = "Invalid username or password !"
        return render_template("deshboard_login.html", parameters = parameters, date = datee)

    elif username==post.username and password==post.password:       # login check
        print("Login into the page !")
        session['user'] = username
        post = Blog_post.query.filter_by().all()
        return render_template("deshboard_data.html",posts = post)
    
    # else redirect to same page
    message ="Invalid username or password !"
    return render_template("deshboard_login.html", parameters = parameters ,date = datee, message=message)

# -----------------------------------------------------------------------------------

@app.route('/file_uploader' ,methods=['GET','POST'])
def file_uploader():
    if 'user' in session:
        if request.method == "POST":
            file = request.files['file']
            file.save( os.path.join( app.config['upload_folder'],(file.filename) ) )
            return "file uploaded sucessfully !"
    return "file not uploaded !"

# ----------------------------------------------------------------------------------

@app.route("/edit_post/<string:id>", methods=['GET','POST'])
def edit_post(id):
    if 'user' in session:
        if request.method == 'POST':
            btitle = request.form.get('title') 
            bstitle = request.form.get('subtitle')
            bcontent = request.form.get('content') 
            bimage = request.form.get('image') 
            bslug = request.form.get('slug') 
            bdate = datetime.now()
            if id =='0':
                post = Blog_post(title=btitle, subtitle=bstitle, content=bcontent, image=bimage, slug=bslug, date=bdate)
                db.session.add(post)
                db.session.commit()
            else:
                post = Blog_post.query.filter_by(id=id).first()
                post.title = btitle
                post.subtitle = bstitle
                post.content = bcontent
                post.image = bimage
                post.slug = bslug
                post.date = bdate
                db.session.commit()
                return redirect(f'/edit_post/{id}')
    post = Blog_post.query.filter_by(id=id).first()
    return render_template("edit_post.html",parameters=parameters, post=post, id=id)

# -------------------------------------------------------------------------------------------

@app.route('/delete_post/<string:id>', methods=['GET', 'POST'])
def delete_post(id):
    if 'user' in session:
        post = Blog_post.query.filter_by(id=id).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/deshboard_login')

# -----------------------------------------------------------------------------------------

@app.route('/register_admin', methods = ['GET',"POST"])
def register_admin():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        rpassword = request.form.get("rpassword")
        if password == rpassword:
            input = admin(username = username, email = email, password = password)
            db.session.add(input)
            db.session.commit()
        else:
            message = "Password not matched !"
            return render_template('register.html',parameters=parameters, message = message)
    return render_template('register.html',parameters=parameters)

#---------------------------------------------------------------------------------------

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/deshboard_login')

# -------------------------------------------------------------------------------------

@app.route("/contact", methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        '''getting data entiry from webpage'''
        nam = request.form.get('name') 
        ema = request.form.get('email')
        pho = request.form.get('phone_no') 
        mes = request.form.get('message') 
        dat = datetime.now()
        '''send to server of sql'''
        data = contects(name = nam, email = ema ,phone_no = pho, message = mes , date = dat) # work as ,
        # INSERT INTO `contects(`id`, `name`, `email`, `phone_no`, `message`, `date`) VALUES (NULL, nam, ema, pho, mes, dat); for put data in sqldataset
        db.session.add(data)
        db.session.commit() 
        '''send mail to to yourself'''
        '''mail.send_message('New message appear in blog contect by '+nam,
                          sender=ema,
                          recipients=[parameters['gmail_user']],
                          body = mes + "\n" + pho
                          )'''
        message = "Thankyou for contact Village Bloger !"
        return render_template("contact.html", parameters = parameters, message=message)
    return render_template("contact.html", parameters = parameters,)

# for run  the url :- ----------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
