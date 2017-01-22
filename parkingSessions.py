#!/usr/bin/python
import stripe
from MySQLdb import *
import time
from datetime import datetime

def getActive(connection, user):
    sessionID = user['parkingSessions'].split(chr(31))
    response = []
    if sessionID != "":
        for i in range(0, len(sessionID)):
            sqlquery = "SELECT * FROM parking_sessions WHERE sessionID = '{0}'".format(sessionID[i])
            result = connection.execute(sqlquery)
            result = connection.fetchone()
            curr = []
            curr.append(result['address'])
            curr.append(result['rego'])
            curr.append(result['expiryTime'])
            response.append(curr)
    return ['0', response]
        

def getVehicles(connection, user):
    vehicleRego = user['rego'].split(chr(31))
    vehicleDescription = user['description'].split(chr(31))
    output = []
    for i in range(len(vehicleRego)-1):
        curr = []
        curr.append(vehicleRego[i])
        curr.append(vehicleDescription[i])
        output.append(curr)
    return ["0", output]
        
    
def createSession(connection, user, rego, coords, charge, CCToken):
    #create a parking session
    stripe.api_key = "sk_test_ksiVjuhEkRActjgc0pjs242S"
    timestamp = int(time.time())
    now = datetime.now()
    timeSinceMidnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() 
    stripe.Charge.create(
          amount=int(charge),
          currency="aud",
          source=CCToken)
    zone = getZone(connection, coords)
    pricing = zone[1]["timing"]
    for i in range(len(pricing)):
        pricing[i] = pricing[i].split('-')
        for j in range(len(pricing[i])):
            pricing[i][j] = pricing[i][j].split(":")
            pricing[i][j] = int(pricing[i][j][1])*3600 + int(pricing[i][j][0])*60
        if timeSinceMidnight > pricing[i][0] and timeSinceMidnight < pricing[i][1]:
           zonePrice = zone[1]["pricing"][i]
    parkTime = zonePrice
    expiryTime = timestamp + (int(charge) / int(zonePrice)) 
    sqlquery = "INSERT INTO parking_sessions (rego, coords, expiryTime, parkingZone) VALUES ('{0}', '{1}', '{2}', '{3}')".format(rego, coords, expiryTime, zone[1]["id"])
    a = connection.execute(sqlquery)
    sessionID = connection.lastrowid
    sqlquery = "UPDATE user_data SET parkingSessions = CONCAT(parkingSessions, '{0}') WHERE user_id = '{1}'".format(str(sessionID)+chr(31), user['user_id'])
    a = connection.execute(sqlquery)
    
    return ['0']
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
def extendSession(connection, rego, charge, CCToken):
    #extend the time left on a parking session
    sqlquery = "UPDATE parking_sessions SET expiryTime = {0} WHERE rego = {1}".format(expiryTime, rego)
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
