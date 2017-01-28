#!/usr/bin/python
import cgi
import cgitb
import os
import base64
import bcrypt
from MySQLdb import *
import time
from signup import *
import stripe
import json

#cgitb.enable()


def login(connection, email, password):
	sqlquery = "SELECT * FROM user_data WHERE email ='{0}'".format(email)
        numRows = connection.execute(sqlquery)
	row =  connection.fetchone()
	if numRows != 0:
		if bcrypt.hashpw(password, row['password']) == row['password']:
			accessToken = base64.b64encode(os.urandom(64))
                        timestamp = int(time.time())
                        token = accessToken + chr(31) + str(timestamp + 3600)
                        sqlquery = "UPDATE user_data SET accessToken = '{0}' WHERE email = '{1}'".format(token, email)
                        a = connection.execute(sqlquery)
                        if row["customer_id"] == "":
                           customerID = createCustomer(connection, row, '', False)
        		return ['0', token]
		else:
			return ['2']
	else:
		return ['1']

def getCustomerInfo(connection, user):
    stripe.api_key = "sk_test_ksiVjuhEkRActjgc0pjs242S"
    if user["customer_id"] != "":
       output = '0'
       customerToken = user["customer_id"].split(chr(31))[0]
       customerInfo = str(stripe.Customer.retrieve(customerToken))
       
    else:
       output = '1'
       customerInfo = ''
    return [output, customerInfo]
