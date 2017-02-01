#!/usr/bin/python
from MySQLdb import *
import cgi
import string
import random   
from twilio.rest import TwilioRestClient
import os
import base64
import bcrypt

def forgotPassword(connection, email):
    form = cgi.FieldStorage()
    #Reset the password in case the user forgets it
    sqlquery = "SELECT * FROM user_data WHERE email = '{0}'".format(email)
    connection.execute(sqlquery)
    user = connection.fetchone()
    retrieveURL = "https://www.parkoo.com.au/oops.html?user={0}".format(user["password"])
    account_sid = "AC63eb049a5e90d3e886e606e575e750f0" # Your Account SID from www.twilio.com/console
    auth_token  = "798d6a444bb25938a1a1217cc47920db"  # Your Auth Token from www.twilio.com/console

    client = TwilioRestClient(account_sid, auth_token)
        
    message = client.messages.create(
          body="Here's your link to reset your password: " + retrieveURL,
          to=user["mobileNumber"],    # Replace with your phone number
          from_="+61428110604") # Replace with your Twilio number
    return ["0", retrieveURL]
    

def resetPassword(connection, token, password):
    hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())
    sqlquery = "UPDATE user_data SET password = '{0}' WHERE password = '{1}'".format(hashedPassword, token)
    connection.execute(sqlquery)
    return ["0"]

'''
def changeNumber(connection):
    #Change the phone number registered to the account
'''

