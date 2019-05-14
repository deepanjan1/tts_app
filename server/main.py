# import flask modules
from flask import Flask, request, redirect, jsonify, url_for

# import for database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Tracks

# import helper functions
from load_articles import loadArticlesAPI, loadArticlesDB
from tts import createAudioFile

# import config modules
from config import POCKET_KEY, ACCESS_TOKEN

# to read APIs
import requests
import json

app = Flask(__name__)

# connect to a postgres database
engine = create_engine('postgres+psycopg2://postgres:password@localhost:5432/tracks')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/tracks')
def getTracks():
    tracks = session.query(Tracks).all()
    track_list = loadArticlesDB(tracks)
    return (track_list)

@app.route('/init')
def initDBWithTracks():
    ''' currently just doing a straight upload into database.
    need to change this to actually only update with new entries'''
    session.query(Tracks).delete()
    tracks = loadArticlesAPI()
    for track in tracks:
        new_track = Tracks(
        key = track['key'],
        title = track['title'],
        text = track['text'],
        image = track['image'],
        percent = track['percent']
        )
        session.add(new_track)
    session.commit()
    return ('Check database, tracks should be initialized')


@app.route('/audio/<string:audio_key>/mp3')
def getAudio(audio_key):
    '''get track text, convert and store audio, output audio file'''
    track = session.query(Tracks).filter_by(key=audio_key).one()
    return (createAudioFile(track.text, audio_key))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
