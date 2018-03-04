from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)
client = MongoClient('localhost', 27017)
db = client['helping-hands']

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
        print(latitude, longitude)
        driversCollection = db.drivers
        driversCollection.update(
            {'userID': data['userID']},
            {'$set': 
                {'GPS': {
                    'lat': latitude,
                    'long': longitude
                }}
            }
        )
        print(data)

api.add_resource(DriverGps, '/driver/gps')
api.add_resource(UpdateIid, '/driver/updateIid')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')