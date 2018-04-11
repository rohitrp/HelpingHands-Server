from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient
import geopy.distance
from gcm import *

import base64
import subprocess
from python_speech_features import mfcc
import scipy.io.wavfile as wav
import os
import numpy as np
from sklearn import svm
from sklearn.utils import shuffle
import pickle


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
        print(data)
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

class IsAmbulance(Resource):
    def post(self):
        data = request.get_json(force=True)
        imgdata = base64.b64decode(data["audio"])

        with open(r"src/tmp.3gp", 'wb') as f:
            f.write(imgdata)

        command = "ffmpeg -y -i ./src/tmp.3gp -ab 160k -ac 2 -ar 44100 -vn ./src/audio.wav"

        subprocess.call(command, shell=True)

        filename = './src/classifier.sav'
        svm_classifier = pickle.load(open(filename, 'rb'))

        (rate, sig) = wav.read(r"src/audio.wav")
        mfcc_feat = mfcc(sig, rate)
        x_test = []
        x_test.append(np.mean(mfcc_feat, axis=0))
        x_test = np.array(x_test)
        prediction = svm_classifier.predict(x_test)
        print (prediction)
        if prediction[0] == 0:
            self.write({"result":"no"})
        else:
            self.write({"result":"yes"})

api.add_resource(DriverGps, '/driver/gps')
api.add_resource(UpdateIid, '/driver/updateIid')
api.add_resource(AmbulanceGps, '/ambulance/gps')
api.add_resource(IsAmbulance, '/isambulance')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')