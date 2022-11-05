from flask import Flask,render_template,url_for,redirect,flash,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, LoginManager, UserMixin
from datetime import datetime
from flask_mail import Mail, Message
import os
"""
To get a 12-digit (any number of choice) secret key, run this in the terminal:
python
import secrets
secrets.token_hex(12)
exit()
Copy the token from the terminal and paste it as the secret key in app.config above
"""

base_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__ )
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'blog.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = '78f51b3cb11851012d6ead66'
db = SQLAlchemy(app)
login_manager = LoginManager(app)


#every signed in user must have the following details
class Users(db.Model, UserMixin):
    __tablename__ = 'user'
 
    id = db.Column(db.Integer(), primary_key=True)
    lnames = db.Column(db.String(255), nullable=False, unique=True)
    fnames = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(10), nullable=False)
    post = db.relationship('JezzyBlog')

   

    def __repr__(self):
        return f"User <{self.username}>"
#contact us schema
class Message(db.Model):
    __tablename__ = 'message'
    
    id = db.Column(db.Integer(), primary_key=True)
    fname= db.Column(db.String(255), nullable=False)
    last= db.Column(db.String(255), nullable=False)
    email1 = db.Column(db.String(255), nullable=False)
    needs= db.Column(db.Text(255), nullable=False)
    text = db.Column(db.String(255))
    def __repr__(self):
        return f"Message <{self.text}>"
#database for all blog to be created what is going to be the content
    
class JezzyBlog(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.String(20), nullable=False, default='N/A')
    posted_on = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow())
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
   
 
    def __repr__(self):
        return self.title

#login manager loader
@login_manager.user_loader
def user_loader(id):
    return Users.query.get(int(id))


#home page non-signed in user
@app.route("/")

def index():
    return render_template('index.html')
#home page for signed in user
@app.route("/home")
def home():
    return render_template('base.html')
#blog page  schema wgere all blog to be created are shown inheriting it content from create,edit,delete
@app.route('/blog')
def blog():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['post']
        post_author = request.form['author']
        post_slug = request.form['slug']
        new_post = JezzyBlog(title=post_title,
                        content=post_content,slug=post_slug, posted_by=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('blog')
    else:
        all_posts = JezzyBlog.query.order_by(JezzyBlog.posted_on).all()
        return render_template('blog.html', blog=all_posts)
# new user signup
@app.route("/signup" ,methods=['GET', 'POST'])
def signup():
     if request.method == 'POST':
        name1=request.form.get('name1')
        name2= request.form.get('name2')
        
        username1 = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password1 = request.form.get('password1')

        user = Users.query.filter_by(username=username1).first()
        if user:
            return redirect(url_for('signup'))

        email_exists = Users.query.filter_by(email=email).first()
        if email_exists:
            return redirect(url_for('signup'))

        password_hash = generate_password_hash(password)

        new_user = Users(username=username1, email=email,lnames=name2,fnames=name1,password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
       

        return redirect(url_for('home'))

     return render_template('register.html')
#logout
@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out of JezzyBlog", category="success")
    return redirect(url_for('index'))
#login
@app.route("/login" ,methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = Users.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        flash("login successful", category="true")
        login_user(user)
        
        return redirect(url_for('home'))
    
   
       

    return render_template('login.html')
  
#create a blog post 
@app.route("/create",methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        post_title = request.form.get('title')
        post_slug= request.form.get('slug')
        post_content = request.form.get('content')
        post_author = request.form.get('author')
        new_post = JezzyBlog(title=post_title,
                        content=post_content, slug = post_slug,posted_by=post_author)
        db.session.add(new_post)
        db.session.commit()
        flash("You have created a new post")
        return redirect(url_for('blog'))
    else:
        all_posts = JezzyBlog.query.order_by(JezzyBlog.posted_on).all()
        return render_template('create.html', blog=all_posts)
    
#about me page 
@app.route("/me")
def me():
    return render_template('me.html')
#edit a blog post from the database
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    to_edit = JezzyBlog.query.get_or_404(id)
    if request.method == 'POST':
        to_edit.title = request.form['title']
        to_edit.slug = request.form['slug']
      
        to_edit.content = request.form['content']
        db.session.commit()
        return redirect(url_for('blog'))
    else:
        return render_template('edit.html', blog=to_edit)
#delete a blog post from the database
@app.route('/delete/<int:id>')
def delete(id):
    to_delete = JezzyBlog.query.get_or_404(id)
    db.session.delete(to_delete)
    flash("You have successfully deleted this post")
    db.session.commit()
    return redirect(url_for('blog'))
#contact form authentication
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        first_names = request.form.get('fname')
        last_names= request.form.get('lname')
        user_email = request.form.get('email')
        user_need = request.form.get('need')
        user_message = request.form.get('message')
        new_contact_message = Message(email1=user_email,
                        fname=first_names,last=last_names, needs=user_need,text=user_message)
        db.session.add(new_contact_message)
        db.session.commit()
        flash("Your message has been succesfully sent")
        return redirect('home')
    else:
        return render_template('contact.html')
        
  
#initilising mydatabase
@app.before_first_request
def create_tables():
    db.create_all()
    
if __name__=="__main__":
    
    app.run(debug=True)