# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import app
from flask_bcrypt import Bcrypt
from flask_app.models import message

bcrypt = Bcrypt(app)
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+[a-zA-Z]+$')
NAME_REGEX = re.compile('[@_!#$%^&*()<>?/\|}{~:1234567890]')
PASSWORD_REGEX = re.compile('[ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890]')

# model the class after the table from our database
class User:
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.messages = []

    # Now we use class methods to query our database
    @classmethod
    def get_all_other_users(cls, data):
        query = 'SELECT * FROM users WHERE id != %(id)s ORDER BY first_name;'
        return connectToMySQL('private_wall_schema').query_db(query, data)

    @classmethod
    def get_all_emails(cls):
        query = 'SELECT email FROM users;'
        # make sure to call the connectToMySQL function with the schema you are targeting.
        results = connectToMySQL('private_wall_schema').query_db(query)
        # Create an empty list to append our instances of table
        user_emails = []
        # Iterate over the db results and create instances of table with cls.
        for user in results:
            user_emails.append( user['email'] )
        return user_emails

    @classmethod
    def save(cls, data):
        query = 'INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW());'
        return connectToMySQL('private_wall_schema').query_db(query, data)

    @classmethod
    def get_user_by_email(cls, data):
        query = 'SELECT * FROM users WHERE email = %(email)s;'
        results = connectToMySQL('private_wall_schema').query_db(query, data)
        if len(results) < 1:
            return False
        return cls(results[0])

    @classmethod
    def get_messages_by_id(cls, data):
        query = "SELECT * FROM users JOIN messages ON messages.user_id = users.id JOIN users AS senders ON senders.id = messages.sender_id WHERE users.id = %(id)s ORDER BY messages.id DESC;"
        results = connectToMySQL('private_wall_schema').query_db(query, data)
        if len(results) > 0:
            target_user = cls( results[0] )
            for row in results:
                data = {
                    "id":row["messages.id"],
                    "content":row["content"],
                    "created_at":row["messages.created_at"],
                    "updated_at":row["messages.updated_at"],
                    "user_id":row["user_id"],
                    "sender_id":row["sender_id"],
                    "sender_fname": row["senders.first_name"],
                    "sender_lname": row["senders.last_name"]
                }

                target_user.messages.append( message.Message(data) )
            return target_user

    @classmethod
    def get_sent_messages_by_id(cls, data):
        query = "SELECT * FROM users JOIN messages ON messages.sender_id = users.id JOIN users AS receivers ON receivers.id = messages.user_id WHERE users.id = %(id)s;"
        results = connectToMySQL('private_wall_schema').query_db(query, data)
        if len(results) > 0:
            target_user = cls( results[0] )
            for row in results:

                data = {
                    "id":row["messages.id"],
                    "content":row["content"],
                    "created_at":row["messages.created_at"],
                    "updated_at":row["messages.updated_at"],
                    "user_id":row["user_id"],
                    "sender_id":row["sender_id"],
                    "sender_fname": row["first_name"],
                    "sender_lname": row["last_name"]
                }

                target_user.messages.append( message.Message(data) )
            return target_user

    @staticmethod
    def validate_registration(data):
        is_valid = True

        if NAME_REGEX.search(data['first_name']) != None or NAME_REGEX.search(data['last_name']) != None:
            flash("Names can not have numbers or special characters.", "registration_error")
            is_valid = False

        if len(data['first_name']) < 2 or len(data['last_name']) < 2:
            flash("First and last name must be at least two characters.", "registration_error")
            is_valid = False
            
        if not EMAIL_REGEX.match(data['email']):
            flash("Invalid email address.", "registration_error")
            is_valid = False

        user_emails = User.get_all_emails()
        for email in user_emails:
            if email == data['email']:
                flash("Email is already registered!", "registration_error")
                is_valid = False
                break

        if len(data['password']) < 8 or PASSWORD_REGEX.search(data['password']) == None:
            flash("Password must be at least 8 characters and contain at least one numer and one uppercase letter.", "registration_error")
            is_valid = False
        
        if data['password'] != data['confirmPassword']:
            flash("Passwords do not match.", "registration_error")
            is_valid = False
        
        return is_valid