import os
import json
import datetime
from bson.json_util import dumps
import requests
from slackclient import SlackClient
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS,cross_origin
from flask import render_template
app = Flask(__name__)
CORS(app)
app.config['MONGO_DBNAME'] = 'zenoffice'
mongo = PyMongo(app)
slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)
config = {
    "on_call": False,
    "polling_frequency_ms": 2000,
    "sound_threshold": 5,
    "hot_threshold": 26,
    "cold_threshold": 17,
    }

@app.route("/")
def dashboard():
    return render_template('dashboard.html')

@app.route("/tts")
def day_tts_data():
    """ Returns TTS data for given day """
    ffrom = request.args.get('from')
    if ffrom is None:
        return jsonify(last_tts_data())
    d = mongo.db.ttss.find({
        "timestamp": {
            "$gt": int(ffrom)
        }
    }, {'_id': False}).sort("timestamp")
    str_data =  dumps(d)
    dict_response = json.loads(str_data)
    outside_temp = get_current_temperature()
    for d in dict_response:
        d.update({'outside_temp': outside_temp})
    return dumps(dict_response)

@app.route("/slack")
def slack():
    slack_message('sshh callense', '#general')
    return "sent"

@app.route("/add_ttss", methods=['POST'])
def add_ttss():
    insert_data = parse_data(json.loads(request.data))
    if insert_data['temperature'] > 100:
        return json.dumps({}), 400, {'Content-Type': 'application/json'}
    mongo.db.ttss.insert_one(insert_data)
    return json.dumps({'success': True}), 200, {'Content-Type': 'application/json'}

def parse_data(raw_data):
    raw_data['timestamp'] = int(datetime.datetime.now().strftime("%s"))
    return raw_data

def last_tts_data():
    cursor = mongo.db.ttss.find({}, {'_id': False}).sort('timestamp', -1).limit(1)
    dict_data = json.loads(dumps(cursor[0]))
    dict_data.update({'outside_temp': get_current_temperature()})
    return dumps(dict_data)

def get_current_temperature():
    CITY_ID = "3433955"
    API_KEY = "c37a488f612d951d0d5615e155299e66"
    WEATHER_API = "http://samples.openweathermap.org/data/2.5/weather?id=%s&appid=%s" % (CITY_ID, API_KEY)
    response = requests.get(WEATHER_API)
    if response.status_code == 200:
        return response.json()['main']['temp'] - 273.15
    return None

@app.route("/configuration", methods=['GET','POST'])
def configuration():
    if request.method == 'GET':
        return fetch_configuration()
    else:
        return set_configuration(request.get_json())

def fetch_configuration():
    return jsonify(config)

def set_configuration(data):
    config.update(data)
    return json.dumps({'success': True}), 200, {'Content-Type': 'application/json'}


def slack_message(text, channel):
    sc.api_call(
      "chat.postMessage",
      channel=channel,
      text=text,
      as_user=True
    )
    return None

if __name__ == "__main__":
    app.run(host='0.0.0.0')
