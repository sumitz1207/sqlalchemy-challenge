import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#setup engine from hawaii sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect using automap base
Base = automap_base()
#table reflect
Base.prepare(engine, reflect=True)

#reference the two tables in Base
Measurement = Base.classes.measurement
Station = Base.classes.station

#start session
session = Session(engine)


#setup flask app
app = Flask(__name__)



# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Climate Analysis Home<br/>"
        f"The List of Available Routes Are:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #precipitation data of last year
    last = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    rain_list = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last).all()

    #create dictionary of rain and return
    return jsonify({date: prcp for date, prcp in rain_list})


@app.route("/api/v1.0/stations")
def stations():
    station_query = session.query(Station.station).all()

    #change station query to list and return
    station_list = list(np.ravel(station_query))
    return jsonify(stations=station_list)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    #calculate temperature observations of last year
    last = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #query of all tobs from the last year
    tobs_query = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= last).all()

    #convert query object to list
    total_tobs = list(np.ravel(tobs_query))

    # results after conversion
    return jsonify(temps=total_tobs)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    #statement to get measurement values
    tempstatement = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        #calculate results for start
        results = session.query(*tempstatement).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    #query runs given both end and start
    results = session.query(*tempstatement).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#run app
if __name__ == '__main__':
    app.run()
