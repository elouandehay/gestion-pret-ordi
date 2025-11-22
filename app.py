from flask import Flask, render_template, request, redirect
from models import *
from config import *
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return "hello, Flask !"

if __name__ == "__main__":
    app.run(debug=True)