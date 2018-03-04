from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class DriverGps(Resource):
    def post(self):
        args = request.get_json(force=True)
        print(args)
        
api.add_resource(DriverGps, '/driver/gps')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')