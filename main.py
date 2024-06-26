from requests.exceptions import ConnectionError
from services.openAI import OpenAI
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS
import os

# ------------------ SETUP ------------------
load_dotenv()
app = Flask(__name__)
# this will need to be reconfigured before taking the app to production
CORS(app, resources={r"/*": {"origins": "*"}})
# ------------------ EXCEPTION HANDLERS ------------------

# Sends response back to Deep Chat using the Response format:
# https://deepchat.dev/docs/connect/#Response
@app.errorhandler(Exception)
def handle_exception(e):
    print(e)
    return {"error": str(e)}, 500

@app.errorhandler(ConnectionError)
def handle_exception(e):
    print(e)
    return {"error": "Internal service error :( )"}, 500

# ------------------ OPENAI API ------------------

open_ai = OpenAI()
@app.route("/1938", methods=["POST"])
def course_1938():
    body = request.json
    return open_ai.chat(body, botID="7369240641248690192")

@app.route("/1980", methods=["POST"])
def course_1980():
    body = request.json
    return open_ai.chat(body, botID="7369239288791924753")

@app.route("/1977", methods=["POST"])
def course_1977():
    body = request.json
    return open_ai.chat(body, botID="7369236869118787600")

# ------------------ START SERVER ------------------

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))