import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy

from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#### Setup Database ####
engine = create_engine("sqlite:///hawaii_database.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#### Setup Flask ####
app = Flask(__name__) 

#### Routes ####
@app.route('/')
def root():
    return """ <h1>Hawaii Climate API</h1>
        <h3>Routes to Use</h3>
        <ul>
            <li>/api/v1.0/precipitation</li>
            <li>/api/v1.0/stations</li>
            <li>/api/v1.0/tobs</li>
            <li>/api/v1.0/temp/{start}</li>
            <li>/api/v1.0/temp/{start}/{end}</li>
        </ul>"""

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Returns precipitation data for the past year"""
    # Create our session (link) from Python to the DB
    # Fix issue with accessing SQLite3 on different threads
    # https://www.reddit.com/r/learnpython/comments/5cwx34/flask_sqlite_error/
    session = Session(engine)

    # Find most recent date in the dataset
    result = session.query(func.max(Measurement.date))[0]
    max_date = result[0]
    last_date = dt.datetime.strptime(max_date, '%Y-%m-%d')

    # Calculate one year ago from the most recent date
    last_year = last_date - dt.timedelta(days=365)

    # Query for results
    results = session.query(Measurement.date, Measurement.prcp).filter(
                        Measurement.date >= last_year).filter(
                        Measurement.date <= last_date).all()

    # Convert results to dictionary
    precipitation = {}
    for result in results:
        (date, prcp) = result
        precipitation[date] = prcp

    # Close the session
    session.close()

    return jsonify({'precipitation': precipitation})

@app.route('/api/v1.0/stations')
def stations():
    """Returns all the station names"""
    # Create our session (link) from Python to the DB
    # Fix issue with accessing SQLite3 on different threads
    # https://www.reddit.com/r/learnpython/comments/5cwx34/flask_sqlite_error/
    session = Session(engine)

    # Query for the result
    results = session.query(Station.name,).group_by(Station.name).all()
    stations = []
    for result in results:
        name = result[0]
        stations.append(name)
    
     # Close the session
    session.close()
    
    return jsonify({'stations': stations})

@app.route('/api/v1.0/tobs')
def tobs():
    """Returns temperature data for the past year"""
    # Create our session (link) from Python to the DB
    # Fix issue with accessing SQLite3 on different threads
    # https://www.reddit.com/r/learnpython/comments/5cwx34/flask_sqlite_error/
    session = Session(engine)

    # Find most recent date in the dataset
    result = session.query(func.max(Measurement.date))[0]
    max_date = result[0]
    last_date = dt.datetime.strptime(max_date, '%Y-%m-%d')

    # Calculate one year ago from the most recent date
    last_year = last_date - dt.timedelta(days=365)

    observations = session.query(
            Measurement.station, func.count(Measurement.station)).group_by(
            Measurement.station).order_by(
            func.count(Measurement.station).desc()).all()

    # Station that has the highest number of observations
    station_name_highest_observations = observations[0][0]

    # Query for results
    results = session.query(Measurement.date, Measurement.tobs).filter(
                        Measurement.date >= last_year).filter(
                        Measurement.date <= last_date).filter(
                        Measurement.station == station_name_highest_observations).all()

    # Convert results to dictionary
    tobs = {}
    for result in results:
        (date, tob) = result
        tobs[date] = tob

    # Close the session
    session.close()

    return jsonify({station_name_highest_observations : tobs})

@app.route('/api/v1.0/temp/<start>', defaults={'end': None})
@app.route('/api/v1.0/temp/<start>/<end>')
def temperatures(start, end):
    """Return TMIN, TAVG, TMAX from a starting date, or between two dates"""
    # Create our session (link) from Python to the DB
    # Fix issue with accessing SQLite3 on different threads
    # https://www.reddit.com/r/learnpython/comments/5cwx34/flask_sqlite_error/
    session = Session(engine)

    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
    query = query.filter(Measurement.date >= start)

    if end is not None:
        query = query.filter(Measurement.date <= end)
    
    # Execute the query
    results = query.all()

    # Pretty up return
    (tmin, tavg, tmax) = results[0]

     # Close the session
    session.close()

    return jsonify({'temp_min' : tmin, 'temp_avg' : tavg, 'temp_max' : tmax})

#### Run ####
if __name__ == '__main__':
    app.run()