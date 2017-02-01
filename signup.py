#!/usr/bin/python
import base64
import bcrypt
from MySQLdb import *
import time
from twilio.rest import TwilioRestClient
from random import randint
import os
import stripe

def verifyMobile(connection, mobileNum, type, fullname, email, password):
    if type == '1':
        verificationDigits = randint(1000, 9999)
        numAvailable = False
        emailAvailable = False
        sqlquery = "SELECT * FROM user_data WHERE mobileNumber = '{0}'".format(mobileNum)
        numRows = connection.execute(sqlquery)
        if numRows == 0 and mobileNum != '':
           numAvailable = True
        sqlquery = "SELECT * FROM user_data WHERE email = '{0}'".format(email)
        numRows = connection.execute(sqlquery)
        if numRows == 0 and mobileNum != '':
           emailAvailable = True
        if emailAvailable and numAvailable:
           account_sid = "AC63eb049a5e90d3e886e606e575e750f0" # Your Account SID from www.twilio.com/console
           auth_token  = "798d6a444bb25938a1a1217cc47920db"  # Your Auth Token from www.twilio.com/console

           client = TwilioRestClient(account_sid, auth_token)
        
           message = client.messages.create(
              body="Here is your Parkoo Verification Number: " + str(verificationDigits),
              to=mobileNum,    # Replace with your phone number
              from_="+61428110604") # Replace with your Twilio number
           return ['0', verificationDigits]
        else:
            return ['1', numAvailable, emailAvailable]
    
    if type == '2':
      timestamp = int(time.time())
      accessToken = base64.b64encode(os.urandom(64))
      accessToken = accessToken+chr(31)+str(timestamp+3600)
      hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())
      timestamp = int(time.time())
      sqlquery = """INSERT INTO user_data (fullname, email,  password, accessToken, mobileNumber)
                                        VALUES ('{0}', '{1}', '{2}','{3}', '{4}')""".format(fullname, email, hashedPassword, accessToken , mobileNum)
      a = connection.execute(sqlquery)
      sqlquery = "SELECT * FROM user_data where email = '{0}'".format(email)
      connection.execute(sqlquery)
      user = connection.fetchone()
      createCustomer(connection, user, "", "")
      output =  ['0', accessToken]
      

  
      return output


def createCustomer(connection, user, CCToken, addCC):
  stripe.api_key = "sk_test_ksiVjuhEkRActjgc0pjs242S"
  if addCC:
     customerToken = user["customer_id"].split(chr(31))
     cu = stripe.Customer.retrieve(customerToken[0])
     cu.sources.create(source=CCToken)
     return ["0", customerToken]
  else:
      newCustomer = stripe.Customer.create(
            description="Customer for "+user["email"],
             email = user["email"]
     )
  
  sqlquery = "UPDATE user_data SET customer_id = '{0}' WHERE user_id = '{1}'".format(newCustomer["id"]+chr(31)+str(addCC), user['user_id'])
  connection.execute(sqlquery)
  return ["0", newCustomer["id"]]
