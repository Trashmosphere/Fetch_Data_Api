from flask import Flask
import spaceObjectsDataAccess

app = Flask(__name__)


@app.route("/objects")
def space_objects_tle():
    return spaceObjectsDataAccess.retrieve_tle_entries()


if __name__ == '__main__':
    app.run(debug=True)

