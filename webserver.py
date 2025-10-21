# webserver.py
from flask import Flask
import os
import news_bot

app = Flask(__name__)

@app.route("/")
def index():
    return "OK - news bot is running"

if __name__ == "__main__":
    # start bot background thread when webserver starts
    news_bot.start_background()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
