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
        Assumes the post data to contain two fields:
        userID, and IID
        """
        data = request.get_json(force=True)
        drivers = db.drivers
        drivers.update(
            {'userID': data['userID']},
            {'$set': {'IID': data['IID']}})
        

class DriverGps(Resource):
    def post(self):
        args = request.get_json(force=True)
        print(args)

api.add_resource(DriverGps, '/driver/gps')
api.add_resource(UpdateIid, '/driver/updateIid')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')