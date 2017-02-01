#!/usr/bin/python
import stripe
from MySQLdb import *
from signup import *
import time
from datetime import datetime

def getActive(connection, user, active):
    sessionID = user['parkingSessions'].split(chr(31))
    response = []
    if sessionID != "":
        for i in range(0, len(sessionID)-1):
            sqlquery = "SELECT * FROM parking_sessions WHERE sessionID = '{0}'".format(sessionID[i])
            result = connection.execute(sqlquery)
            result = connection.fetchone()
            if  result != None:
                curr = []
                if active == "True":
                   if int(result["expiryTime"]) > int(time.time()):
                      curr.append(eval(result["coords"]))
                      #curr.append(eval(result["startTime"]))
                      curr.append(result["expiryTime"])
                      curr.append(result["rego"])
                      curr.append(result["sessionID"])
                      response.append(curr)
                else:
                   #curr.append("Expiry: "+str(int(result["expiryTime"])-int(time.time())))  
                   curr.append(eval(result["coords"]))
                   #curr.append(eval(result["startTime"]))
                   curr.append(result["expiryTime"]) 
                   curr.append(result["rego"]) 
                   curr.append(result["sessionID"])
                   response.append(curr)
    return ['0', response]
        

def getVehicles(connection, user):
    vehicleRego = user['rego'].split(chr(31))
    vehicleDescription = user['description'].split(chr(31))
    output = []
    if user["rego"] != "":
        for i in range(len(vehicleRego)-1):
            curr = []
            curr.append(vehicleRego[i])
            curr.append(vehicleDescription[i])
            output.append(curr)
    return ["0", output]
        
    
def createSession(connection, user, rego, coords, charge, CardID):
    #create a parking session
    stripe.api_key = "sk_test_ksiVjuhEkRActjgc0pjs242S"
    timestamp = int(time.time())
    now = datetime.now()
    timeSinceMidnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    customerToken = user["customer_id"].split(chr(31)) 
    cu = stripe.Customer.retrieve(customerToken[0])
    cu.default_source = CardID
    cu.save()
    stripe.Charge.create(
        amount=int(charge),
        currency="aud",
        customer = customerToken[0],
        receipt_email=user["email"],
        description="charge for "+user["email"])
    zone = getZone(connection, coords)
    pricing = zone[1]["timing"]
    for i in range(len(pricing)):
        pricing[i] = pricing[i].split('-')
        for j in range(len(pricing[i])):
            pricing[i][j] = pricing[i][j].split(":")
            pricing[i][j] = eval(pricing[i][j][1])*3600 + eval(pricing[i][j][0])*60
        if timeSinceMidnight > pricing[i][0] and timeSinceMidnight < pricing[i][1]:
           zonePrice = zone[1]["pricing"][i]
    parkTime = zonePrice
    chargeDollars = float(charge)/100
    duration  = (chargeDollars / zonePrice)*3600 
    expiryTime = timestamp + duration
    sqlquery = "INSERT INTO parking_sessions (rego, coords, expiryTime, duration, startTime,  parkingZone) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(rego, coords, expiryTime, duration, timestamp, zone[1]["id"])
    a = connection.execute(sqlquery)
    sessionID = connection.lastrowid
    sqlquery = "UPDATE user_data SET parkingSessions = CONCAT(parkingSessions, '{0}') WHERE user_id = '{1}'".format(str(sessionID)+chr(31), user['user_id'])
    a = connection.execute(sqlquery)
    
    return ['0', charge, chargeDollars, duration, zonePrice]

def deleteSession(connection, user, rego):
    #delete a parking session
    sqlquery = "SELECT * FROM parking_sessions WHERE rego = {0}".format(rego)
    response = connection.execute(sqlquery)
    session = connection.fetchone()
    sessionID = session['sessionID']
    sqlquery = "DELETE * FROM parking_sessions WHERE rego = {0}".format(rego)
    a = connection.execute(sqlquery)
    sessions = user['parkingSessions'].split(chr(31))
    newSessions = []
    for i in range(len(sessions)):
        if sessions[i] != sessionID:
            newSessions.append(sessions[i])
            
    sqlquery = "UPDATE user_data SET parkingSessions = {0} WHERE user_id = {1}".format(chr(31).join(newSessions), user['user_id'])
    a = connection.execute(sqlquery)
    
    return ['0']
def extendSession(connection, user, sessionID, charge, CardID):
    #extend the time left on a parking session
    stripe.api_key = "sk_test_ksiVjuhEkRActjgc0pjs242S"
    customerToken = user["customer_id"].split(chr(31))
    cu = stripe.Customer.retrieve(customerToken[0])
    cu.default_source = CardID
    cu.save()
    stripe.Charge.create(
        amount=int(charge),
        currency="aud",
        customer = customerToken[0],
        receipt_email=user["email"],
        description="charge for "+user["email"])
    sqlquery = "SELECT * FROM parking_sessions WHERE sessionID = {0}".format(sessionID)
    connection.execute(sqlquery)
    session =  connection.fetchone()
    sqlquery = "SELECT * FROM zones WHERE id = '{0}'".format(session["parkingZone"])
    connection.execute(sqlquery)
    zone = connection.fetchone()
    now = datetime.now()
    timeSinceMidnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    pricing = eval(zone["timing"])
    for i in range(len(pricing)):
        pricing[i] = pricing[i].split('-')
        for j in range(len(pricing[i])):
            pricing[i][j] = pricing[i][j].split(":")
            pricing[i][j] = int(pricing[i][j][1])*3600 + int(pricing[i][j][0])*60
            if timeSinceMidnight > pricing[i][0] and timeSinceMidnight < pricing[i][1]:
               zonePrice = eval(zone["pricing"])[i]
    chargeDollars = float(charge)/100
    duration  = (chargeDollars / zonePrice)*3600  
    expiryTime = float(session["expiryTime"]) + duration 
    sqlquery = "UPDATE parking_sessions SET expiryTime = {0} WHERE sessionID = {1}".format(expiryTime , sessionID)
    a = connection.execute(sqlquery)
    
    return ['0']
def getZone(connection, coords):
    #get the zone the car is currently in
    sqlquery = "SELECT * FROM zones"
    numZones = connection.execute(sqlquery)
    zones = connection.fetchall()
    for i in range (0, numZones):
        zone = zones[i]
        inZone = pointInPolygon(coords, zone["corners"])
        if inZone[1] == True:
           output = {}
           output["id"] = zone["id"]
           output["timing"] = eval(zone["timing"])
           output["pricing"] = eval(zone["pricing"])
           return ["0", output]
        else:
           output = -1

    
    return ["0", output]

def pointInPolygon(coords, poly):
    coords = eval(coords)
    x = coords[0]
    y = coords[1]
    poly = eval(poly)
    polyCorners = len(poly)
    j = polyCorners -1
    oddNodes= False
    for i in range(0 , polyCorners):
        if (poly[i][1]<y and poly[j][1]>=y) or (poly[j][1]<y and poly[i][1]>=y):
            if (poly[i][0]+(y-poly[i][1])/(poly[j][1]-poly[i][1])*(poly[j][0]-poly[i][0])<x):
                oddNodes=not(oddNodes)
        j=i
    
    return ['0', oddNodes]
