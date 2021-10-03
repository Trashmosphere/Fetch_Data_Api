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