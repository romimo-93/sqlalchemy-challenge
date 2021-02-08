import numpy as np
import pandas as pd
import datetime as dt


from flask import Flask, jsonify

import matplotlib.pyplot as plt
# %matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import os
import sys

from scipy import stats
from numpy import mean


print(os.path.dirname(__file__))

root_project_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, root_project_path)

hawaii_path = os.path.join(root_project_path, "hawaii.sqlite")

# engine = create_engine("sqlite:///hawaii.sqlite", echo=False)
engine = create_engine("sqlite:///"+hawaii_path)

Base = automap_base()
Base.prepare(engine, reflect=True)
print(f"FIND ME {Base.classes.keys()}")

hawaii_measurement = Base.classes.measurement
hawaii_station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to my 'Home' page!:<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = session.query(hawaii_measurement.date, hawaii_measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    # prcp_values = list(np.ravel(results))
    # return jsonify(prcp_values)

    all_measurements = []
    for date, prcp in results:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        all_measurements.append(measurement_dict)

    return jsonify(all_measurements)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    results = session.query(hawaii_station.station).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/temperature")
def temperature():
    session = Session(engine)
    station_temp_year_ago = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    station_temp = session.query(hawaii_measurement.date, hawaii_measurement.tobs).\
        filter(hawaii_measurement.station == 'USC00519281').\
        filter(hawaii_measurement.date >= station_temp_year_ago).\
        order_by(hawaii_measurement.date).all()
    
    station_tobs = list(np.ravel(station_temp))
    return jsonify(station_tobs)

@app.route("/api/v1.0/start/<start>")
def start_date(start):
    session = Session(engine)

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    start_temp_data = [func.min(hawaii_measurement.tobs), func.max(hawaii_measurement.tobs), func.avg(hawaii_measurement.tobs)]

    start_temp_list = (session.query(*start_temp_data)
        .filter(func.strftime('%Y-%m-%d', hawaii_measurement.date) >= start_date)
        .all())
        

    start_dates = []
    for temp in start_temp_list:
        start_dict = {}
        start_dict["Min Temp"] = temp[0]
        start_dict["Max Temp"] = temp[1]
        start_dict["Avg Temp"] = temp[2]
        start_dates.append(start_dict)

    return jsonify(start_dates)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)

    new_start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()

    start_end_temp_data = [func.min(hawaii_measurement.tobs), func.max(hawaii_measurement.tobs), func.avg(hawaii_measurement.tobs)]

    start_end_temp_list = (session.query(*start_end_temp_data).\
        filter(hawaii_measurement.date >= new_start_date).
        filter(hawaii_measurement.date <= end_date).all())

    session.close()

        
    # start_end_temp_results = [{"Min Temp":temp[0],"Max Temp":temp[1],"Avg Temp":temp[2]} for temp in start_end_temp_list]

    start_end_temp_results = list(np.ravel(start_end_temp_list))
    min_temp = start_end_temp_results[0]
    max_temp = start_end_temp_results[1]
    avg_temp = start_end_temp_results[2]
    

    start_end_list = []

    all_dates_dict = [{"Min Temp":min_temp},
                      {"Max Temp":max_temp},
                      {"Avg Temp":avg_temp}]
    
    start_end_list.append(all_dates_dict)
    return jsonify(start_end_list)
        
  

if __name__ == '__main__':
    app.run(debug=False)