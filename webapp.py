import os
import json
from slackclient import SlackClient
from flask import Flask, request
from flask_pymongo import PyMongo
from flask import render_template
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'zenoffice'
mongo = PyMongo(app)
slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)

@app.route("/")
def dashboard():
    return render_template('dashboard.html')

@app.route("/<year>/<month>/<day>")
def day_tts_data():
    """ Returns TTS data for given day """
    return

@app.route("/slack")
def slack():
    sc.api_call(
      "chat.postMessage",
      channel="#general",
      text="Shhhh! Estan en call!",
      as_user=True
    )
    return "sent"


@app.route("/add_ttss", methods=['POST'])
def add_ttss():
    insert_data = parse_data(request.get_json(silent=True))
    mongo.db.ttss.insert_one(insert_data)
    return json.dumps({'success': True}), 200, {'Content-Type': 'application/json'}

def parse_data(raw_data):
    # TODO transformar el timestamp en algo que podamos usar
    # TODO parsear el volumen y la temperatura si hace falta
    return raw_data

if __name__ == "__main__":
    app.run(host='0.0.0.0')
