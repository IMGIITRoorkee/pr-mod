import os
import docker
import constants


from flask import redirect, url_for, session, request
from git import Repo
from app import app, github
from config import Config
from parser import parse
from helpers import (
    id_generator,
    find_free_port,
    get_pull_request_info,
    execute_testfile)


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


@app.route('/git_pull/<oauth_token>/<user>/<owner>/<repo>/<branch>')
def git_pull_repo(oauth_token, user, owner, repo, branch):
    """ Pulls a repo from github and changes the branch.
    :param token: Authorization token for user.
    :type token: String
    :param user: Authorized User.
    :type user: String
    :param owner: Repository Owner.
    :type owner: String
    :param repo: Name of the github repository.
    :type repo: String
    :param branch: Branch of the PR owner.
    :type branch: String
    :returns: Redirects to deploy_dind.
    """
    # name of the cloned repository on server
    repo_name = "{0}-{1}".format(repo, id_generator())
    try:
        # Clone the forked repository
        remote_url = constants.remote_url_string.format(user, repo)
        https_remote_url = constants.https_url_string.format(
            oauth_token,
            remote_url)
        Repo.clone_from(https_remote_url, repo_name)
    except KeyError:
        # Fork doesnot exist, Clone from main repository
        remote_url = constants.remote_url_string.format(owner, repo)
        https_remote_url = constants.https_url_string.format(
            oauth_token,
            remote_url)
        Repo.clone_from(https_remote_url, repo_name)
  
    # change branch in the cloreponed repository
    os.chdir(repo_name)  # changes dir to the cloned repo
    os.system('git checkout {}'.format(branch))
    os.chdir('../')  # change back to the pwd
    return redirect(
        url_for(
            'deploy_dind',
            oauth_token=oauth_token,
            repo=repo_name)
        )


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
    repo = session.get('repo_url')
    user, owner, repo, branch = get_pull_request_info(oauth_token, repo)
    return redirect(
        url_for(
            'git_pull_repo',
            oauth_token=oauth_token,
            user=user,
            owner=owner,
            repo=repo,
            branch=branch)
        )


@app.route('/deploy-dind/<oauth_token>/<repo>')
def deploy_dind(oauth_token, repo):
    """ Deploys an isolated `Docker-In-Docker` environment and
    mounts the pulled repository to the container.
    :param oauth_token: Authorization token for Owner.
    :type oauth_token: String
    :param repo: Name of the cloned github repository.
    :type repo: String
    """
    # to ssh into container use `docker exec -ti exodus /bin/sh`
    test_file_params = parse(repo, oauth_token)
    client = docker.from_env()
    try:
        volume = test_file_params['VOL']
    except KeyError:
        volume = '/{}'.format(repo)
    try:
        cwd = test_file_params['CWD']
    except KeyError:
        cwd = '/'
    # ToDo: Generate port mapping
    vol_host = os.getcwd() + "/{}".format(repo)
    name = "exdous-{}".format(id_generator())
    dind_env = client.containers.run(
        'prmod/base-image',
        name=name,
        ports={'8088/tcp': 8000},
        volumes={
            vol_host: {
                'bind': volume,
                'mode': 'rw'
            }
        },
        working_dir=cwd,
        privileged=True,
        detach=True)
    execute_testfile(dind_env, test_file_params)
    return redirect("http://localhost:8000")


# Implement logout function
@app.route('/logout')
def logout():
    return "Logout"


if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY
    app.run()
