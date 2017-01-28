#!/usr/bin/python
import cgi
import cgitb
import json
import time
import os
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs/'
os.environ['PYTHON_EGG_DIR']='/tmp/.python-eggs/'
from MySQLdb import *
from signup import *
from login import *
from addVehicle import *
from parkingSessions import *
#from forgot import *
cgitb.enable() 					    #Error checking I think?
form = cgi.FieldStorage()			#Sets up getting post data


db = connect(host="localhost",user="root", passwd="parkoo",db="parkoo", cursorclass=cursors.DictCursor)
cursor = db.cursor()
surpress = cursor.execute("USE parkoo")

def handleRequest():
    print "Content-type: text/plain"
    print "Access-Control-Allow-Origin: *"
    print ""
    accessToken = form.getvalue('accessToken')
    type = form.getvalue('req_type')
    if type != None:
        if type == 'signup':
            output = signup(cursor,form.getvalue('fullname'),form.getvalue('email'),form.getvalue('mobileNum'),form.getvalue('password'))
        elif type == 'login':
            output = login(cursor, form.getvalue('email'),form.getvalue('password'))
        elif type == 'verifyMobile1':
            output = verifyMobile(cursor, form.getvalue('mobileNum'), '1', None, form.getvalue('email'), None)
        elif type == 'verifyMobile2':
            output = verifyMobile(cursor, form.getvalue('mobileNum'), '2', form.getvalue('fullname'), form.getvalue('email'), form.getvalue('password')) 
        else:
            sqlquery = "SELECT * FROM user_data WHERE accessToken = '{0}'".format(accessToken)
            accessResponse = cursor.execute(sqlquery)
            user =  cursor.fetchone()
            if accessResponse != 0:
                accessToken = user['accessToken'].split(chr(31))
                timestamp = int(time.time())
                if accessToken[1] > timestamp:
                    if type == 'addVehicle':
                        output = addVehicle(cursor, user ,form.getvalue('rego'), form.getvalue('description') , form.getvalue('photo'))
                    elif type == 'editVehicle':
                         output = editVehicle(cursor, user ,form.getvalue('rego'), form.getvalue('description') , form.getvalue('photo'))
                    elif type =='deleteVehicle':
                        output = deleteVehicle(cursor, user, form.getvalue('rego'))
                    elif type == 'getCustomerInfo':
                        output = getCustomerInfo(cursor, user)
                    elif type == 'getActive':
                        output = getActive(cursor, user, form.getvalue('active'))
                    elif type == 'createSession':
                        output = createSession(cursor, user, form.getvalue('rego'), form.getvalue('coords'), form.getvalue('charge'), form.getvalue('CCToken'))
                    elif type == 'deleteSession':
                        output = deleteSession(cursor, user, form.getvalue('rego'))
                    elif type == 'extendSession':
                        output = extendSession(cursor, form.getvalue('rego'), form.getvalue('charge'), form.getvalue('CCToken'))
                    elif type == 'getZone':
                        output = getZone(cursor, form.getvalue('coords'))
                    elif type == 'getVehicles':
                        output = getVehicles(cursor, user)
                    elif type == 'createCustomer':
                        output = createCustomer(cursor, user, form.getvalue('CCToken'),form.getvalue('addCC'))

                else:
                    output = ['1', "out of time"]
            else:
                output = ['1', "doesnt exist", accessToken]
    
        if output[0] == '0':
            if type != 'login' and type != 'signup':
                timestamp = int(time.time())
                #sqlquery = "UPDATE user_data SET accessToken = '{0}' WHERE user_id = '{1}'".format(accessToken[0]+chr(31)+str(timestamp+3600), user['user_id'])
                #a = cursor.execute(sqlquery)
    else:
        output = ['Invalid Request Type']
        
    db.commit()
    print json.dumps(output)



handleRequest()
