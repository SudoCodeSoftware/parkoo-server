#!/usr/bin/python
import cgi
import cgitb
import os
import base64
import bcrypt
from MySQLdb import *
import time

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
        		return ['0', token]
		else:
			return ['2']
	else:
		return ['1']
