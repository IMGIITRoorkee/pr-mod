import os

from flask import redirect, url_for, session, request
from git import Repo
from app import app, github
from config import Config


@app.route('/', methods=['POST'])
def index():
    """ Redirects to authorize a user/org.
    """
    session['remote_url'] = request.args.get('remote')
    return redirect('/authorize')


@app.route('/git_pull')
def git_pull_repo():
    """ Pulls a repo from github.
    :returns: Url for the deployed application.
    :rtype: string  
    """
    https_remote_url = 'https://{0}:x-oauth-basic@{1}'.format(
        session.get('token'),
        session.get('remote_url')
        )
    repo_name = '<repo_name>'
    cloned_repo = Repo.clone_from(https_remote_url, repo_name)
    # generate url for deployed app
    return '<app_url>'


@app.route('/authorize')
def authorize():
    """ Authorizes user with defined scope.
    """
    return github.authorize(scope=Config.scope)


@app.route('/callback')
@github.authorized_handler
def authorization_callback(oauth_token):
    """ Callback function after user authorization.
    :param access_token: Authorization token for the logged in user.
    :type access_token: string
    :returns: Redirects to git-pull function.  
    """
    if oauth_token is None:
        return "User Not Authenticated"
    session['token'] = oauth_token
    # Start a DIND enviroment before pull 
    return redirect('/git_pull')


if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY
    app.run()
