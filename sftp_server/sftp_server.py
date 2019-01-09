"""Stand up a SFTP server"""

import threading
import socket
import paramiko
from .ssh_interface import SSHInterface
from .sftp_interface import SFTPInterface


class SFTPServer(object):
    """
    Stand up a SFTP server

    :param file_path: Unix path to be served as the SFTP `root` directory
    :type file_path: string

    :param rsa_key_path: Unix path to a RSA host key for server to authenticates
    itself (i.e. `ssh-keygen -t rsa -N '' -f host_key`)
    :type host_key_path: string

    :param get_user: A method that returns a User object that has two methods
     `has_read_access` and `has_write_access`.  Each method should accept a unix path
     (relative to `file_path`) and return True or False appropriately.
     Users should also have a sensible `__str__` representation for use in logging.
    :type user: method
    """

    SOCKET_BACKLOG = 10

    def __init__(self, file_path, rsa_key_path, get_user=None):
        self.file_path = file_path
        self.host_key = paramiko.RSAKey.from_private_key_file(rsa_key_path)
        if get_user is not None:
            self.get_user = get_user

    def start_server(self, host, port):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(self.SOCKET_BACKLOG)
        while True:
            conn = s.accept()[0]
            self.start_sftp_session(conn)

    def get_user(self, username, password):
        raise NotImplementedError()

    def start_sftp_session(self, conn):
        transport = paramiko.Transport(conn)
        transport.add_server_key(self.host_key)
        transport.set_subsystem_handler(
            "sftp", paramiko.SFTPServer, SFTPInterface, self.file_path
        )
        transport.start_server(
            server=SSHInterface(self.get_user), event=threading.Event()
        )
