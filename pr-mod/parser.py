import os
from collections import OrderedDict


def find(name, path):
    """ Finds the path of the Testfile.
    :param name: Name of the Testfile.
    :type name: string
    :param path: path of the repo to search for Testfile.
    :type path: string
    :return: Path of the Testfile.
    :rtype: string
    """
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def parse(repo):
    """ Parses and extracts cmd from `Testfile`.
    :param repo: Name of the cloned repository.
    :type repo: string
    :return CMD: Dictonary of extracted commands.
    :rtype: JSON
    """
    path = find("Testfile", os.getcwd()+"/{}".format(repo))
    # ToDo: demo testfile for testing purpose, remove in production.
    if path is None:
        test_file = open("Testfile", "r")
    else:
        test_file = open(path, "r")
    content = test_file.read()
    file_lines = content.split("\n")
    filtered_file_lines = [
        lines for lines in file_lines if lines != '' and not lines.startswith(
            "#")]
    CMD = OrderedDict()
    for lines in filtered_file_lines:
        command_type, command = lines.split(" ", 1)
        CMD[command_type] = command
    if 'PORTS' in CMD:
        CMD['PORTS'] = [x for x in CMD['PORTS'].split(" ")]
    return CMD
