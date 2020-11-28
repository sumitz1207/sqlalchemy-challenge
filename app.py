import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#setup engine from hawaii sqlite in resources folder
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect using automap base
Base = automap_base()
#table reflect
Base.prepare(engine, reflect=True)

#reference the two tables in Base
Measurement = Base.classes.measurement
Station = Base.classes.station


#setup flask app
app = Flask(__name__)



# Flask Routes and welcome text
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
    session = Session(engine)

    # Query for the date and precipitation for the last year
    rain_list = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last).all()
    session.close()

    #create dictionary of rain and return
    rain_dict = {date: prcp for date, prcp in rain_list}
    return jsonify(rain_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_query = session.query(Station.station).all()
    session.close()
    #change station query to list and return
    station_list = list(np.ravel(station_query))
    return jsonify(stations=station_list)


@app.route("/api/v1.0/tobs")
def temperatures():
    #calculate temperature observations of last year
    last = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    session = Session(engine)

    #query of all the tobs from the last year
    tobs_query = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= last).all()
    session.close()

    #convert query object to list
    total_tobs = list(np.ravel(tobs_query))

    # results after conversion
    return jsonify(temps=total_tobs)


@app.route("/api/v1.0/temp/<start>")
def startonly(start=None):
    #statement to get measurement values
    tempstatement = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    session = Session(engine)

    #calculate results for start
    temp_query = session.query(*tempstatement).filter(Measurement.date >= start).all()
    session.close()

    list_temperature = list(np.ravel(temp_query))
    return jsonify(list_temperature)


@app.route("/api/v1.0/temp/<start>/<end>")
def startend(start=None, end=None):
    #statement to get measurement values
    tempstatement2 = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    session = Session(engine)

    #query runs given both end and start
    temp_query2 = session.query(*tempstatement2).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    list_temperature2 = list(np.ravel(temp_query2))
    return jsonify(list_temperature2)

#run app
if __name__ == '__main__':
    app.run()