# 1. import Flask
from flask import Flask, jsonify, request
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
import numpy as np
import pandas as pd

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurment = Base.classes.measurement
Station = Base.classes.station

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/></br>"
        f"Precipitation by Date </br>"
        f"/api/v1.0/precipitation</br></br>"
        f"Stations<br/>"
        f"/api/v1.0/stations</br></br>"
        f"Temperature observations</br>"
        f"/api/v1.0/tobs</br></br>"
        f"Highest, average, and lowest temperatures for a given range</br>"
        f"Start_date should be included in URL in the following format (end_date is optional):</br> "       
        f"/api/v1.0/start_end?start_date=yyyy-mm-dd&end_date=yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperatures by Date"""
    session.query(Measurment.date).order_by(Measurment.date.desc()).first()
    #return the data
    data =session.query(Measurment.date, Measurment.prcp).\
        filter(Measurment.date > '2016-08-23').\
        order_by(Measurment.date).all()

    session.close()
    
    precp_by_date = []
    for date, prcp in data:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precp_by_date.append(precip_dict)
                          
    return jsonify(precp_by_date)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all passengers
    stations = session.query(Measurment.station).\
        group_by(Measurment.station).all()
       
    session.close()

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temps():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of Temperatures for the most action station for the last year of data"""
    # Query all passengers
    temps = session.query(Measurment.date,Measurment.tobs).\
        order_by(Measurment.date.desc()).\
        filter(Measurment.station == 'USC00519281').\
        filter(Measurment.date > '2016-08-23').all()
    session.close()

    return jsonify(temps)

@app.route("/api/v1.0/start_end")
def start_end():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    if 'start_date' in request.args:
        start_date = str(request.args['start_date'])
    else: 
        start_date = "2010-01-01"
    if 'end_date' in request.args:
        end_date = str(request.args['end_date'])
    else: 
        end_date = "2017-08-23"


    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range"""
    # Query all passengers
    start_end = session.query(func.min(Measurment.tobs), func.avg(Measurment.tobs), func.max(Measurment.tobs)).\
        filter(Measurment.date >= start_date).\
        filter(Measurment.date <= end_date).all()
    session.close()

    temp_list = []
    for tmin, tavg, tmax in start_end:
        temp_dict = {}
        temp_dict["tmin"] = tmin
        temp_dict["tavg"] = tavg
        temp_dict["tmax"] = tmax
        temp_list.append(temp_dict)
                          
    return jsonify(temp_list)
    

if __name__ == '__main__':
    app.run(debug=True)
