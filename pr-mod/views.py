import os

from flask import session, redirect
from git import Repo
from app import app, github
from config import Config

@app.route('/')
def index():
    if session.get('token') is None:
        return redirect('/authorize')
    
    # Start a DIND enviroment before pull 
    return redirect('/git_pull')

@app.route('/git_pull')
def git_pull_repo():
    https_remote_url = 'https://{0}:x-oauth-basic@{1}'.format(
        session.get('token'),
        # repo remote URL
    )
    repo_name = '<repo_name>'
    cloned_repo = Repo.clone_from(https_remote_url, repo_name)
    
    # generate url for deployed app
    return '<app_url>'

@app.route('/authorize')
def login():
    return github.authorize(scope=Config.scope)

@app.route('/callback')
@github.authorized_handler
def authorized(oauth_token):
    if oauth_token is None:
        return "User Not Authenticated"
    session['token'] = oauth_token
    return redirect('/')

if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY
    app.run()
