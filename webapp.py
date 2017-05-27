import os
import json
from bson.json_util import dumps
import datetime
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
    return jsonify(str_data)

@app.route("/slack")
def slack():
    slack_message('sshh callense', '#general')
    return "sent"

@app.route("/add_ttss", methods=['POST'])
def add_ttss():
    insert_data = parse_data(request.get_json(silent=True))
    mongo.db.ttss.insert_one(insert_data)
    return json.dumps({'success': True}), 200, {'Content-Type': 'application/json'}

def parse_data(raw_data):
    raw_data['timestamp'] = datetime.datetime.now().strftime("%s")
    return raw_data

def last_tts_data():
    cursor = mongo.db.ttss.find({}, {'_id': False}).sort('timestamp', -1).limit(1)
    return dumps(cursor)


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
