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

# Create our session (link) from Python to the DB
session = Session(engine)

#### Setup Flask ####
app = Flask(__name__) 

#### Routes ####
@app.route('/')
def root():
    return """ <h1>Hawaii Climate API</h1>
        <h3>Routes to Use</h3>
        <ul>
            <li>api/v1.0/precipitation</li>
            <li>api/v1.0/stations</li>
            <li>api/v1.0/tobs</li>
            <li>api/v1.0/{start}</li>
            <li>api/v1.0/{start}/{end}</li>
        </ul>"""

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Returns precipitation data for the past year"""
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

    return jsonify(precipitation)

#### Run ####
if __name__ == '__main__':
    app.run()