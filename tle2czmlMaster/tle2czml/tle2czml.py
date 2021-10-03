''' generates .czml file or json used to visualize the satellites orbits '''

import math
from datetime import datetime, timedelta

import pkg_resources
import pytz
from dateutil import parser
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

from .czml import (CZML, Billboard, CZMLPacket, Description, Label, Path,
                   Position)

BILLBOARD_SCALE = 1.5
LABEL_FONT = "11pt Lucida Console"
SATELITE_IMAGE_URI =("data:image/png;base64,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")
MULTIPLIER = 60
DESCRIPTION_TEMPLATE = 'Orbit of Satellite: '
MINUTES_IN_DAY = 1440
TIME_STEP = 300

DEFAULT_RGBA = [213, 255, 0, 255]
DEBUGGING = False


class Satellite:
    'Common base class for all satellites'

    def __init__(self, raw_tle, tle_object, rgba):
        self.raw_tle = raw_tle
        self.tle_object = tle_object  # sgp4Object
        self.rgba = rgba
        self.sat_name = raw_tle[0].rstrip()
        # extracts the number of orbits per day from the tle and calcualtes the time per orbit
        self.orbital_time_in_minutes = (
            24.0/float(self.raw_tle[2][52:63]))*60.0
        self.tle_epoch = tle_object.epoch

    def get_satellite_name(self):
        'Returns satellite name'
        return self.sat_name

    def get_tle_epoch(self):
        'Returns tle epoch'
        return self.tle_epoch



class Colors:
    'defines rgba colors for satellites'

    def __init__(self):
        path = 'rgba_list.txt'
        filepath = pkg_resources.resource_filename(__name__, path)
        colors_file = open(filepath, 'r')

        rgbs = []

        for color in colors_file:
            rgb = color.split()
            rgb.append(255)  # append value for alpha
            rgbs.append(rgb)

        self.rgbs = rgbs
        self.index = 0

    def get_next_color(self):
        'returns next color'
        next_color = self.rgbs[self.index]
        if self.index < len(self.rgbs) - 1:
            self.index += 1
        else:
            self.index = 0

        return next_color

    def get_rgbs(self):
        'returns rgbs'
        return self.rgbs


# create CZML doc with default document packet
def create_czml_file(start_time, end_time):
    'create czml file using start_time and end_time'
    interval = get_interval(start_time, end_time)
    doc = CZML()
    packet = CZMLPacket(id='document', version='1.0')
    print(interval)
    print(start_time.isoformat())

    packet.clock = {"interval": interval, "currentTime": start_time.isoformat(
    ), "multiplier": MULTIPLIER, "range": "LOOP_STOP", "step": "SYSTEM_CLOCK_MULTIPLIER"}
    doc.packets.append(packet)
    return doc


def create_satellite_packet(sat, sim_start_time, sim_end_time):
    'Takes a satelite and returns its orbit'
    availability = get_interval(sim_start_time, sim_end_time)
    packet = CZMLPacket(id='Satellite/{}'.format(sat.sat_name))
    packet.availability = availability
    packet.description = Description("{} {}".format(DESCRIPTION_TEMPLATE, sat.sat_name))
    packet.billboard = create_bill_board()
    packet.label = create_label(sat.sat_name, sat.rgba)
    packet.path = create_path(availability, sat, sim_start_time, sim_end_time)
    packet.position = create_position(sim_start_time, sim_end_time, sat.tle_object)
    return packet


def create_bill_board():
    'returns a billboard'
    bill_board = Billboard(scale=BILLBOARD_SCALE, show=True)
    bill_board.image = SATELITE_IMAGE_URI
    return bill_board


def create_label(sat_id, rgba):
    'creates a label'
    lab = Label(text=sat_id, show=True)
    lab.fillColor = {"rgba": rgba}
    lab.font = LABEL_FONT
    lab.horizontalOrigin = "LEFT"
    lab.outlineColor = {"rgba": [0, 0, 0, 255]}
    lab.outlineWidth = 2
    lab.pixelOffset = {"cartesian2": [12, 0]}
    lab.style = 'FILL_AND_OUTLINE'
    lab.verticalOrigin = 'CENTER'
    return lab


def create_path(total_path_interval, sat, sim_start_time, sim_end_time):
    'creates a lead and trailing path'
    path = Path()

    path.show = [{"interval": total_path_interval, "boolean": False}]
    path.width = 1
    path.material = {"solidColor": {"color": {"rgba": sat.rgba}}}
    path.resolution = 120

    start_epoch_str = total_path_interval.split("/")[0]

    minutes_in_sim = int((sim_end_time - sim_start_time).total_seconds()/60)

    left_over_minutes = minutes_in_sim % sat.orbital_time_in_minutes
    number_of_full_orbits = math.floor(minutes_in_sim/sat.orbital_time_in_minutes)

    sub_path_interval_start = parser.parse(start_epoch_str)
    # first interval roughly half an orbit, rest of the path intervals are full orbits
    sub_path_interval_end = sub_path_interval_start + timedelta(minutes=left_over_minutes)
    sub_path_interval_str = (sub_path_interval_start.isoformat() + '/' +
                             sub_path_interval_end.isoformat())

    orbital_time_in_seconds = (sat.orbital_time_in_minutes * 60.0)

    if DEBUGGING:
        # goes from tle epoch to 12/24 hours in future
        print('Total Path Interval: ' + total_path_interval)

    lead_or_trail_times = []

    for _ in range(number_of_full_orbits + 1):
        lead_or_trail_times.append({
            "interval": sub_path_interval_str,
            "epoch": sub_path_interval_start.isoformat(),
            "number": [
                0, orbital_time_in_seconds,
                orbital_time_in_seconds, 0
            ]
        })

        if DEBUGGING:
            print('Sub interval string: ' + sub_path_interval_str)

        sub_path_interval_start = sub_path_interval_end
        sub_path_interval_end = (sub_path_interval_start +
                                 timedelta(minutes=sat.orbital_time_in_minutes))
        sub_path_interval_str = (sub_path_interval_start.isoformat() + '/' +
                                 sub_path_interval_end.isoformat())

    path.leadTime = lead_or_trail_times

    if DEBUGGING:
        print()

    sub_path_interval_start = parser.parse(start_epoch_str)
    # first interval roughly half an orbit, rest of the path intervals are full orbits
    sub_path_interval_end = sub_path_interval_start + timedelta(minutes=left_over_minutes)
    sub_path_interval_str = (sub_path_interval_start.isoformat() + '/' +
                             sub_path_interval_end.isoformat())

    lead_or_trail_times = []

    for _ in range(number_of_full_orbits + 1):
        lead_or_trail_times.append({
            "interval": sub_path_interval_str,
            "epoch": sub_path_interval_start.isoformat(),
            "number":[
                0, 0,
                orbital_time_in_seconds, orbital_time_in_seconds
            ]
        })

        if DEBUGGING:
            print('Sub interval string: ' + sub_path_interval_str)

        sub_path_interval_start = sub_path_interval_end
        sub_path_interval_end = (sub_path_interval_start +
                                 timedelta(minutes=sat.orbital_time_in_minutes))

        sub_path_interval_str = (sub_path_interval_start.isoformat() + '/' +
                                 sub_path_interval_end.isoformat())

    path.trailTime = lead_or_trail_times

    return path

def create_position(start_time, end_time, tle):
    'creates a position'
    pos = Position()
    pos.interpolationAlgorithm = "LAGRANGE"
    pos.interpolationDegree = 5
    pos.referenceFrame = "INERTIAL"
    pos.epoch = start_time.isoformat()

    diff = end_time - start_time
    number_of_positions = int(diff.total_seconds()/300)
    # so that there's more than one position
    number_of_positions += 5
    pos.cartesian = get_future_sat_positions(
        tle, number_of_positions, start_time)
    return pos


def get_interval(current_time, end_time):
    'creates an interval string'
    return current_time.isoformat() + "/" + end_time.isoformat()


def get_future_sat_positions(sat_tle, number_of_positions, start_time):
    'returns an array of satellite positions'
    time_step = 0
    output = []
    for _ in range(number_of_positions):
        current_time = start_time + timedelta(seconds=time_step)
        eci_position, _ = sat_tle.propagate(current_time.year, current_time.month, current_time.day,
                                            current_time.hour, current_time.minute,
                                            current_time.second)

        output.append(time_step)
        output.append(eci_position[0] * 1000)  # converts km's to m's
        output.append(eci_position[1] * 1000)
        output.append(eci_position[2] * 1000)
        time_step += TIME_STEP

    return output


def get_satellite_orbit(raw_tle, sim_start_time, sim_end_time, czml_file_name):
    'returns orbit of the satellite'
    tle_sgp4 = twoline2rv(raw_tle[1], raw_tle[2], wgs72)

    sat = Satellite(raw_tle, tle_sgp4, DEFAULT_RGBA)
    doc = create_czml_file(sim_start_time, sim_end_time)

    if DEBUGGING:
        print()
        print('Satellite Name: ', sat.get_satellite_name)
        print('TLE Epoch: ', sat.tle_epoch)
        print('Orbit time in Minutes: ', sat.orbital_time_in_minutes)
        print()

    sat_packet = create_satellite_packet(sat, sim_start_time, sim_end_time)
    doc.packets.append(sat_packet)
    with open(czml_file_name, 'w') as file:
        file.write(str(doc))


def read_tles(tles: str, rgbs):
    'reads tle from string'
    raw_tle = []
    sats = []

    i = 1
    for line in tles.splitlines():
        raw_tle.append(line)

        if i % 3 == 0:
            tle_object = twoline2rv(raw_tle[1], raw_tle[2], wgs72)
            sats.append(Satellite(raw_tle, tle_object, rgbs.get_next_color()))
            raw_tle = []
        i += 1

    return sats


def tles_to_czml(tles, start_time=None, end_time=None, silent=False):
    """
    Converts the contents of a TLE file to CZML and returns the JSON as a string
    """
    rgbs = Colors()
    satellite_array = read_tles(tles, rgbs)

    if not start_time:
        start_time = datetime.utcnow().replace(tzinfo=pytz.UTC)

    if not end_time:
        end_time = start_time + timedelta(hours=24)

    doc = create_czml_file(start_time, end_time)

    for sat in satellite_array:
        sat_name = sat.sat_name
        orbit_time_in_minutes = sat.orbital_time_in_minutes
        tle_epoch = sat.tle_epoch

        if not silent:
            print()
            print('Satellite Name: ', sat_name)
            print('TLE Epoch: ', tle_epoch)
            print('Orbit time in Minutes: ', orbit_time_in_minutes)
            print()

        sat_packet = create_satellite_packet(sat, start_time, end_time)

        doc.packets.append(sat_packet)

    return str(doc)


def create_czml(inputfile_path, outputfile_path=None, start_time=None, end_time=None):
    """
    Takes in a file of TLE's and returns a CZML file visualising their orbits.
    """
    
    with open(inputfile_path, 'r') as tle_src:
        #print(tle_src.read())
        doc = tles_to_czml(
            tle_src.read(), start_time=start_time, end_time=end_time)
        if not outputfile_path:
            outputfile_path = "orbit.czml"
        with open(outputfile_path, 'w') as file:
            file.write(str(doc))
    

def db_create_czml(inputData, start_time=None, end_time=None):
    doc=tles_to_czml(inputData, start_time=start_time, end_time=end_time)
    return str(doc)