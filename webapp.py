import os
from slackclient import SlackClient
from flask import Flask
from flask import render_template
app = Flask(__name__)
slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)

@app.route("/")
def hello():
    return render_template('dashboard.html')

@app.route("/slack")
def slack():
    sc.api_call(
      "chat.postMessage",
      channel="#general",
      text="Shhhh! Estan en call!"
    )
    return "sent"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
