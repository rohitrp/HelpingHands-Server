from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient
import geopy.distance
from gcm import *

app = Flask(__name__)
api = Api(app)
client = MongoClient('localhost', 27017)
db = client['helping-hands']

class AmbulanceGps(Resource):
    def post(self):
        """
        Assumes the POST data to contain two fields:
        userID, and IID
        """
        data = request.get_json(force=True)
        latitude, longitude = data['GPS'].split(',')

        ambulanceDriversCollection = db.ambulanceDrivers
        ambulanceDriversCollection.update(
            {'userID': data['userID']},
            {'$set': {
                'GPS': {
                    'lat': latitude,
                    'long': longitude
                }        
            }},
            upsert=True
        )

        #TODO: find all drivers withing 1 KM of ambulance's location        
        latitude = float(latitude)
        longitude = float(longitude)
        
        driversCollection = db.drivers

        drivers = driversCollection.find({})

        nearbyDriversIID = []
        for driver in drivers:
            driverLat = float(driver['GPS']['lat'])
            driverLong = float(driver['GPS']['long'])

            dist = geopy.distance.vincenty((latitude, longitude), (driverLat, driverLong)).km
            
            # Check if distance is less than 5 kms
            if (dist < 400):
                nearbyDriversIID += [driver['IID']]

        print(nearbyDriversIID)
        gcm = GCM("AIzaSyAzclIVV1T7AI_tS2_Uhxrq3cK1zde33E8")
        response = gcm.json_request(registration_ids=nearbyDriversIID,data ={'msg': "Happy Birthday!"})
        print(response)

class UpdateIid(Resource):
    def post(self):
        """
        Assumes the POST data to contain two fields:
        userID, and IID
        """
        data = request.get_json(force=True)
        driversCollection = db.drivers
        driversCollection.update(
            {'userID': data['userID']},
            {'$set': {'IID': data['IID']}}, 
            upsert=True
        )        

class DriverGps(Resource):
    def post(self):
        """
        Assumes the POST data to contain two fields:
        userID, GPS
        """
        data = request.get_json(force=True)
        latitude, longitude = data['GPS'].split(',')

        driversCollection = db.drivers
        driversCollection.update(
            {'userID': data['userID']},
            {'$set': 
                {'GPS': {
                    'lat': latitude,
                    'long': longitude
                }}
            },
            upsert=True
        )

api.add_resource(DriverGps, '/driver/gps')
api.add_resource(UpdateIid, '/driver/updateIid')
api.add_resource(AmbulanceGps, '/ambulance/gps')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')