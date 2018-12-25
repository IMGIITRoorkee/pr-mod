import string
import random
import socket

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
    free_port =  sock.getsockname()[1]
    s.close()
    return free_port