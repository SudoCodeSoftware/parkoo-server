#!/usr/bin/python
import base64
import bcrypt
from PIL import *
from MySQLdb import *

def addVehicle(connection, user, rego, description , photo):
    sqlquery = "UPDATE user_data SET rego = CONCAT(rego, '{0}') WHERE user_id = '{1}'".format(rego+chr(31), user['user_id'])
    a = connection.execute(sqlquery)
    if description == None:
       description = "No Description"
    sqlquery = "UPDATE user_data SET description = CONCAT(description, '{0}') WHERE user_id = '{1}'".format(description+chr(31), user['user_id'])
    a = connection.execute(sqlquery)
    #sqlquery = "UPDATE user_data SET photo = CONCAT(photo, {0})".foromat(photopath+chr(31))
    #a = connection.execute(sqlquery)
    return ['0']
    
    
