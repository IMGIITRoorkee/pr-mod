import os
import requests
import json

from flask import redirect, url_for, session, request
from git import Repo
from app import app, github
from config import Config


@app.route('/<owner>/<repo>/pull/<pr_no>')
def index(owner, repo, pr_no):
    """ Redirects to authorize a user/org.
    :param owner: Owner of the github repository.
    :type owner:  string
    :param repo: name of the github repository.
    :type repo: string
    :param pr_no: pull request no. for the repository.
    :type pr_no: string
    :return redirect object. 
    """
    session['repo'] = repo
    session['repo_url'] = "{0}repos/{1}/{2}/pulls/{3}".format(
        Config.GITHUB_BASE_URL,
        owner,
        repo,
        pr_no)
    return redirect('/authorize')


@app.route('/git_pull/<oauth_token>/<user>/<repo>/<branch>')
def git_pull_repo(oauth_token, user, repo, branch):
    """ Pulls a repo from github.
    :param token: Authorization token for user.
    :type token: String
    :param user: Authorized User.
    :type remote_url: String
    :param repo: Name of the github repository.
    :type repo: String
    :param branch: Branch of the PR owner.
    :type branch: String
    :returns: Url for the deployed application.
    :rtype: string  
    """
    remote_url = "github.com/{0}/{1}.git".format(user, repo)
    https_remote_url = 'https://{0}:x-oauth-basic@{1}'.format(
        oauth_token,
        remote_url
        )
    repo_name = repo
    cloned_repo = Repo.clone_from(https_remote_url, repo_name)
    return 'Repo Cloned Successfully'


@app.route('/authorize')
def authorize():
    """ Authorizes user with defined scope.
    """
    return github.authorize(scope=Config.scope)


def get_remote_url(oauth_token):
    """ Gets remote details.
    :param oauth_token: Authorization token for Owner.
    :type oauth_token: String
    :return tuple of remote url and git branch name.
    :rtype tuple object
    """
    response = requests.get(
        session.get('repo_url'),
        auth  = (Config.GITHUB_USER, oauth_token)
    )
    json_data = json.loads(response.text)
    return (
        json_data['head']['user']['login'],
        json_data['base']['repo']['name'],
        json_data['head']['ref']
    )


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
    user, repo, branch = get_remote_url(oauth_token)
    return redirect(
        url_for(
            'git_pull_repo',
            oauth_token=oauth_token,
            user=user,
            repo=repo,
            branch=branch)
        )


if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY
    app.run()
