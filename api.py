from tle2czmlMaster.tle2czml.tle2czml import create_czml

def converter(tleFilePath, czmlFilePath):
    create_czml(tleFilePath,czmlFilePath)

converter("C:/Hackathon NASA/data/testData.tle", 'C:/Hackathon NASA/data/newCzml.czml')