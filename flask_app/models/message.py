# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
# model the class after the table from our database
class Message:
    def __init__( self , data ):
        self.id = data['id']
        self.content = data['content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.sender_id = data['sender_id']
        self.sender_fname = data['sender_fname']
        self.sender_lname = data['sender_lname']
    # Now we use class methods to query our database

    @classmethod
    def send_message(cls, data):
        query = 'INSERT INTO messages (content, user_id, sender_id, created_at, updated_at) VALUES (%(content)s, %(user_id)s, %(sender_id)s, NOW(),NOW());'
        return connectToMySQL('private_wall_schema').query_db(query, data)

    @classmethod
    def delete(cls, data):
        query = 'DELETE FROM messages WHERE id = %(id)s;'
        return connectToMySQL('private_wall_schema').query_db(query, data)