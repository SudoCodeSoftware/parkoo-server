#!/usr/bin/python
import base64
import bcrypt
from PIL import *
from MySQLdb import *

def addVehicle(connection, user, rego, description , photo):
    regos = user["rego"]
    if rego in regos:
       return ["1"]
    sqlquery = "UPDATE user_data SET rego = CONCAT(rego, '{0}') WHERE user_id = '{1}'".format(rego+chr(31), user['user_id'])
    a = connection.execute(sqlquery)
    if description == None:
       description = "No Description"
    sqlquery = "UPDATE user_data SET description = CONCAT(description, '{0}') WHERE user_id = '{1}'".format(description+chr(31), user['user_id'])
    a = connection.execute(sqlquery)
    #sqlquery = "UPDATE user_data SET photo = CONCAT(photo, {0})".foromat(photopath+chr(31))
    #a = connection.execute(sqlquery)
    return ['0']


def editVehicle(connection, user, rego, description, photo):
   regos = user["rego"]
   descriptions = user["description"]
   for i in range(len(regos)):
      if regos[i] == rego:
         regos[i] = rego
         descriptions[i] = description
   
   sqlquery = "UPDATE user_data SET rego = '{0}', description = '{1}' WHERE user_id = '{1}'".format(regos, descriptions, user['user_id'])
   connection.execute(sqlquery)
   return["0"]

def deleteVehicle(connection, user, rego):
   regos = user["rego"]
   descriptions = user["description"]
   newRegos = []
   newDescriptions = []
   for i in range(len(regos)):
      if regos[i] != rego:
         newRegos.append(regos[i])
         newDescriptions.append(descriptions[i])
   
   sqlquery = "UPDATE user_data SET rego = '{0}', description = '{1}' WHERE user_id = '{1}'".format(newRegos, newDescriptions, user['user_id'])
   connection.execute(sqlquery)
   return["0"]

