import os
from slackclient import SlackClient
from flask import Flask
app = Flask(__name__)
slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/slack")
def slack():
    sc.api_call(
      "chat.postMessage",
      channel="#general",
      text="Shhhh! Estan en call!",
      as_user=True
    )
    return "sent"

if __name__ == "__main__":
    app.run()
