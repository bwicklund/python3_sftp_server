"""Paramiko SSH Interface Overides"""

import paramiko
import logging


class SSHInterface(paramiko.ServerInterface):
    """
    Paramiko SSH Interface overides, injects our own auth method.

    :param get_user: A method that returns a User object that has two methods
    `has_read_access` and `has_write_access`.  Each method should accept a unix path
    (relative to `file_path`) and return True or False appropriately.
    Users should also have a sensible `__str__` representation for use in logging.
    :type get_user: method
    """

    def __init__(self, get_user):
        self.get_user = get_user

    def check_auth_password(self, username, password):
        user = self.get_user(username, password)
        if user:
            logging.info(("Auth successful for %s" % username).encode("utf-8"))
            self.user = user
            return paramiko.AUTH_SUCCESSFUL
        else:
            logging.info(("Auth failed for %s" % username).encode("utf-8"))
            return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        else:
            return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
