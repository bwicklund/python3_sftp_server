import paramiko
import os
from .clean_response import clean_response

class SFTPFileHandle(paramiko.SFTPHandle):
    """
    Override a couple of methods in SFTPHandle
    """
    @clean_response
    def chattr(self, path, attr):
        # Pretend that this has been executed. But do nothing.
        pass

    @clean_response
    def stat(self):
        return paramiko.SFTPAttributes.from_stat(
                os.fstat(self.readfile.fileno()))
