from requests.exceptions import ConnectionError
from services.openAI import OpenAI
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS

# ------------------ SETUP ------------------

load_dotenv()

app = Flask(__name__)

# this will need to be reconfigured before taking the app to production
cors = CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://coze-deepchat-proxy-server-production.up.railway.app"]}})

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

@app.route("/1938", methods=["POST", "OPTIONS"])
def course_1938():
    if request.method == 'OPTIONS':
        return '', 200
    body = request.json
    return open_ai.chat(body, botID="7342365921484292098")

@app.route("/1980", methods=["POST", "OPTIONS"])
def course_1980():
    if request.method == 'OPTIONS':
        return '', 200
    body = request.json
    return open_ai.chat(body, botID="7342365921484292098")

@app.route("/1977", methods=["POST", "OPTIONS"])
def course_1977():
    if request.method == 'OPTIONS':
        return '', 200
    body = request.json
    return open_ai.chat(body, botID="7342365921484292098")

# ------------------ START SERVER ------------------

if __name__ == "__main__":
    app.run(port=5000)