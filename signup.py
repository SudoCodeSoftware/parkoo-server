#!/usr/bin/python
import base64
import bcrypt
from MySQLdb import *
import time
from twilio.rest import TwilioRestClient
from random import randint
import os

def signup(connection, fullname, email, mobileNum, password):
	sqlquery = "SELECT * FROM user_data WHERE email = '{0}'".format(email)
	numRows = connection.execute(sqlquery)
	if numRows == 0 and email != '':
		sqlquery = "SELECT * FROM user_data WHERE mobileNumber = '{0}'".format(mobileNum)
		numRows = connection.execute(sqlquery)
		if numRows == 0 and mobileNum != '':
			accessToken = base64.b64encode(os.urandom(64))
                        hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())
                        timestamp = int(time.time())
			sqlquery = """INSERT INTO user_data (fullname, email,  password, accessToken, mobileNumber)
					 VALUES ('{0}', '{1}', '{2}','{3}', '{4}')""".format(fullname, email, hashedPassword, accessToken+chr(31)+str(timestamp+3600), mobileNum)
        		a = connection.execute(sqlquery)
			output =  ['0', accessToken]
		else:
			output = ['2']
	else:
		output = ['1']
	return output

def verifyMobile(connection, user, digits, type):
    if type == '1':
        mobileNum = user['mobileNumber']
        verificationDigits = randint(1000, 9999)
        
        sqlquery = "UPDATE user_data SET parkingSessions = {0} WHERE user_id = {1}".format(verificationDigits, user['user_id'])
        
        account_sid = "AC97d17d05b2488280dd9f9b8321758ede" # Your Account SID from www.twilio.com/console
        auth_token  = "3e5d1831a1e26710075d688e1b1727c4"  # Your Auth Token from www.twilio.com/console

        client = TwilioRestClient(account_sid, auth_token)
        
        message = client.messages.create(
            body=verificationDigits,
            to="+61447429557",    # Replace with your phone number
            from_="+61429544348") # Replace with your Twilio number
        return ['0', verificationDigits]
        #print(message.sid)
        
    if type == '2':
        if digits == user["parkingSessions"]:
            return ['0']
        else:
            return ['1']
            
        
