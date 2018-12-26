import string
import random
import socket
import json
import requests

from config import Config


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """ Generates a random string.
    :param size: Length of random string.
    :type size: Int
    :param chars: Charectors used for random string generation.
    :type chars: String
    :return: String, random string.
    """
    return ''.join(random.choice(chars) for _ in range(size))


def find_free_port():
    """ Finds a free port on the server.
    :return port : free port no.
    :rtype: Integer
    """
    sock = socket.socket()
    sock.bind(('', 0))
    free_port = sock.getsockname()[1]
    s.close()
    return free_port


def get_remote_url(oauth_token, repo):
    """ Gets remote details.
    :param oauth_token: Authorization token for Owner.
    :type oauth_token: String
    :param repo: Name of the Github repository.
    :type repo: String
    :return tuple of remote url and git branch name.
    :rtype tuple object
    """
    response = requests.get(
        repo,
        auth=(Config.GITHUB_USER, oauth_token)
    )
    json_data = json.loads(response.text)
    return (
        json_data['head']['user']['login'],
        json_data['base']['repo']['owner']['login'],
        json_data['base']['repo']['name'],
        json_data['head']['ref']
    )


def execute_testfile(oauth_token, container, test_file_params):
    """ Setups environment inside `prmod\base-image` container.
    :param oauth_token: Authorization token for the user.
    :type oauth_token: String
    :param container: docker container for app-environment.
    :type container: Docker object
    :param test_file_params: Parsed Testfile cmd.
    :type test_file_params: UnorderDict Obj
    """
    # execute Testfile cmds in `prmod\base-image`
    for cmd in test_file_params:
        print(test_file_params[cmd])
        if cmd == 'CMD':
            # execute git cmd
            git_cmd = test_file_params[cmd].replace("git clone https://", "")
            git_cmd = "git clone https://{0}:x-oauth-basic@{1}".format(
                oauth_token,
                git_cmd)
            container.exec_run(git_cmd)
        elif cmd == 'SHELL':
            # execute shell cmd
            container.exec_run(test_file_params[cmd])
        elif cmd == 'DOCKER':
            # execute docker cmd
            container.exec_run(test_file_params[cmd])
