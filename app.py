from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserRegisterForm, UserLoginForm
from werkzeug.exceptions import Unauthorized


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_app_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def root():
    """Home page root"""
    return redirect('/register')


@app.route('/secret')
def secret_page():
    """Home page root"""

    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    return "You made it!"


@app.route('/users/<username>')
def user_page(username):
    """Show user info page"""
    if 'username' in session and username != session['username']:
        flash("You don't have access to this user page!", "danger")
        return redirect('/')
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    user = User.query.get_or_404(username)
    return render_template('users/user.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserRegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f"/users/{username}")

    return render_template('users/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        
        if user:
            session['username'] = user.username
            return redirect(f"/users/{username}")

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete user"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")


########## Feedback Routes #################

# @app.route('/users/<username>')
# def user_page(username):
#     user = User.query.get_or_404(username)
#     return render_template('users/user.html', user=user)