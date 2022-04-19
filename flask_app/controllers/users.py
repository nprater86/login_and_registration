# from crypt import methods
from datetime import datetime
from flask_app import app
from flask import render_template,redirect,request,session,flash
from flask_app.models.user import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=["POST"])
def register():
    #if the user submitted their registration
    if request.form["which_form"] == 'register':
        #first validate the data
        if not User.validate_registration(request.form):
            return redirect('/')

        #if valid, hash the password
        pw_hash = bcrypt.generate_password_hash(request.form['password'])

        #pass data into data dictionary
        data = {
            "first_name":request.form["first_name"],
            "last_name":request.form["last_name"],
            "email":request.form["email"],
            "password": pw_hash
            }

        #pass data dictionary to method that creates user
        User.save(data)

        #store user data in session for user in success page
        new_user = User.get_user_by_email(data)

        session['id'] = new_user.id
        session['first_name'] = new_user.first_name
        session['last_name'] = new_user.last_name
        session['email'] = new_user.email

        #redirect to the success page
        return redirect('/dashboard')

    #if the user submitted their login information:
    if request.form["which_form"] == 'login':
        data = {"email":request.form["email"]}

        target_user = User.get_user_by_email(data)

        if not target_user:
            flash("Invalid Email/Password", "login_error")
            return redirect('/')

        if not bcrypt.check_password_hash(target_user.password, request.form['password']):
            flash("Invalid Email/Password", "login_error")
            return redirect("/")
        
        session['id'] = target_user.id
        session['first_name'] = target_user.first_name
        session['last_name'] = target_user.last_name
        session['email'] = target_user.email

        return redirect('/dashboard')
    
    return ('/')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect('/')

    now = datetime.now()

    users = User.get_all_other_users(session)
    data = {"id":session["id"]}
    user_messages = User.get_messages_by_id(data)
    user_sent = User.get_sent_messages_by_id(data)

    return render_template('dashboard.html', users=users, user_messages = user_messages, user_sent = user_sent, now=now)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
