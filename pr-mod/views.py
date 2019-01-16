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
    execute_testfile
)


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

    if Config.users["default"] == "deny" and owner not in Config.users["allow"]:
        return redirect('404/Permission_Denied')
    elif Config.users["default"] == "allow" and owner in Config.users["deny"]:
        return redirect('404/Permission_Denied')
    else:
        session['repo'] = repo
        session['pr_no'] = pr_no
        session['repo_url'] = "{0}repos/{1}/{2}/pulls/{3}".format(
            Config.GITHUB_BASE_URL,
            owner,
            repo,
            pr_no
        )
        print("logging: Authorizing github user")
        return redirect('/authorize')


@app.route('/git_pull/<user>/<owner>/<repo>/<branch>')
def git_pull_repo(user, owner, repo, branch):
    """ Pulls a repo from github and changes the branch.
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
    oauth_token = session.get('oauth_token')
    print("logging: Pulling Repository from github")
    # name of the cloned repository on server
    repo_name = "{0}-{1}".format(repo, id_generator())
    session['repo_name'] = repo_name
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
    print("logging: Repo pull complete")
    # change branch in the cloreponed repository
    os.chdir(repo_name)  # changes dir to the cloned repo
    os.system('git checkout {}'.format(branch))
    os.chdir('../')  # change back to the pwd
    return redirect(
        url_for(
            'deploy_dind',
            oauth_token=oauth_token,
            repo=repo_name,
            branch=branch)
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
    print("logging: User Authenticated")
    session['oauth_token'] = oauth_token
    repo = session.get('repo_url')
    user, owner, repo, branch = get_pull_request_info(oauth_token, repo)
    if (session.get('oauth_token') is True and
        session.get('{0}-{1}'.format(repo, branch)) is True):
            return redirect(session.get('{0}-{1}'.format(
                repo,
                session.get('pr_no')))
            )
    return redirect(
        url_for(
            'git_pull_repo',
            oauth_token=oauth_token,
            user=user,
            owner=owner,
            repo=repo,
            branch=branch)
        )


@app.route('/deploy-dind/<repo>/<branch>')
def deploy_dind(repo, branch):
    """ Deploys an isolated `Docker-In-Docker` environment and
    mounts the pulled repository to the container.
    :param oauth_token: Authorization token for Owner.
    :type oauth_token: String
    :param repo: Name of the cloned github repository.
    :type repo: String
    :param branch: Branch for the pull request.
    :type branch: String
    """
    oauth_token = session.get('oauth_token')
    name = "exdous-{}".format(id_generator())
    # to ssh into container use `docker exec -ti <name> /bin/sh`
    print("logging: Reading Testfile config")
    test_file_params = parse(repo, oauth_token)
    print("logging: Testfile config read")
    client = docker.from_env()
    try:
        volume = test_file_params['VOL']
        vol_host = os.getcwd() + "/{}".format(repo)
    except KeyError:
        volume = '/{}'.format(repo)
    try:
        cwd = test_file_params['CWD']
    except KeyError:
        cwd = '/'
    print("logging: find free port for the application")
    try:
        port = test_file_params['PORTS']
        free_port = find_free_port(1)[0]
    except KeyError:
        return redirect("404/Ports_Not_Mentioned")
    print("logging: will accept tcp request on port: {}".format(free_port))
    print("logging: deploying prmod/base-image")
    dind_env = client.containers.run(
        'prmod/base-image',
        name=name,
        ports={port: free_port},
        volumes={
            vol_host: {
                'bind': volume,
                'mode': 'rw'
            }
        },
        working_dir=cwd,
        privileged=True,
        detach=True)
    session['container'] = dind_env
    print("logging: prmod/base-image deployed")
    execute_testfile(dind_env, test_file_params)
    print("logging: application deployed on server")
    url = "{}:{}".format(Config.SERVER_IP, port)
    session['{0}-{1}'.format(repo, session.get('pr_no'))] = url
    return redirect(url)


@app.route('/logout')
def logout():
    container = session.get('container')
    repo = session.get('repo_name')
    print("logging: closing pulled docker image")
    container.close()
    print("logging: removing cloned repository from server")
    os.system("rm -rf {}".format(repo))
    return "Logout"


@app.route('/404/<error>')
def not_found(error):
    return error


if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY
    app.run(ssl_context=('cert.pem', 'key.pem'))
