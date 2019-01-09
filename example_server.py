#!/usr/bin/env python
import logging
import os

from sftp_server.sftp_server import SFTPServer

SSH_PORT = 2222
FILE_ROOT = os.path.realpath('/Users/bwicklun/Projects')
HOST_KEY = os.path.join(os.path.dirname(__file__), 'host_key')

# Example Auth System...
def get_user(username, password):
  class User(object):

      def __init__(self, username):
          self.username = username

      def has_read_access(self, path):
          return True

      def has_write_access(self, path):
          return True

      def __str__(self):
          return '<%s>' % self.username

  if username == 'bwicklun' and password == 'password!':
    return User(username)
  else:
    return None

if __name__ == '__main__':
    server = SFTPServer(FILE_ROOT, HOST_KEY, get_user=get_user)
    server.start_server('0.0.0.0', SSH_PORT)
