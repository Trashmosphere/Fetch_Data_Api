from os import read
from tle2czmlMaster.tle2czml.tle2czml import create_czml, db_create_czml
from flask import Flask
from flask_cors import CORS, cross_origin
import spaceObjectsDataAccess

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/objects")
@cross_origin()
def space_objects_tle():
    ##create_czml("C:/Hackathon NASA/data/testData.tle",'C:/Hackathon NASA/data/newCzml.czml')
    #return "dada"
    tleData=open("C:/Hackathon NASA/data/testData.tle", "r")

    return db_create_czml(tleData.read())

def converter(tleFilePath, czmlFilePath):
    result = spaceObjectsDataAccess.retrieve_tle_entries()
    create_czml(result,czmlFilePath)

@app.route("/test")
@cross_origin()
def test():
    return "DA"

if __name__ == '__main__':
    app.run(debug=True)

