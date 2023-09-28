# Import the dependencies.

import numpy as np


import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify




#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """ list all available api routes."""
    return (
        f"Available Route.<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    query_date = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    precepitation_values = [{date: prcp} for date, prcp in query_date]
    return jsonify(precepitation_values)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    all_station = []
    for id, station_code, name, latitude, longitude, elevation in results:
        station_dict = {
            'Id': id,
            'station': station_code,
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation
        }
        all_station.append(station_dict)
    return jsonify(all_station)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    year_back = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Fetch temperature observations for the last year
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_back).all()
    session.close()

    stats_tobs = [{"date": date, "tobs": tobs} for date, tobs in results]
    return jsonify(stats_tobs)

@app.route("/api/v1.0/<start>/<end>")
def temps_calcs(start, end):
    session = Session(engine)

    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date.between(start, end)).first()
    session.close()

    # Check if we have data for the given date range
    if not results or None in results:
        return jsonify({"error": "No data available for the given date range."}), 404

    temp_tobs = {
        "Min_Temp": results[0],
        "avg_Temp": results[1],
        "max_Temp": results[2]
    }
    return jsonify(temp_tobs)

@app.route("/api/v1.0/<start>")
def temps(start):
    return temps_calcs(start, dt.datetime.now().strftime('%Y-%m-%d'))

if __name__ == '__main__':
    app.run(debug=True)
    














