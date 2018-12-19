from flask import Flask
from flask_github import GitHub

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

github = GitHub(app)
