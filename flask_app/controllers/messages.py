from flask_app import app
from flask import render_template,redirect,request,session,flash
from flask_app.models.message import Message

@app.route('/send_message', methods=["POST"])
def send_message():
    if request.form["user_id"] == 'default':
        flash("Make selection!", "send_message")
        return redirect('/dashboard')
    data = {
        "user_id": request.form["user_id"],
        "content": request.form["content"],
        "sender_id": session["id"]
    }

    Message.send_message(data)

    return redirect('/dashboard')

@app.route('/delete_message', methods=["POST"])
def delete_message():
    data = {
        "id": request.form["message_id"]
    }
    Message.delete(data)
    return redirect('/dashboard')