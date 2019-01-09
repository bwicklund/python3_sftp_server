"""Paramiko SFTP Interface Overides"""

import errno
import paramiko
import os
from .log_it import log_it
from .clean_response import clean_response
from .sftp_file_handle import SFTPFileHandle

class PermissionDenied(Exception):
    pass

class SFTPInterface(paramiko.SFTPServerInterface):
    FILE_MODE = 0o664
    DIRECTORY_MODE = 0o775

    def __init__(self, server, root):
        self.user = server.user
        self.root = root

    def realpath_for_read(self, path):
        return self._realpath(path, self.user.has_read_access)

    def realpath_for_write(self, path):
        return self._realpath(path, self.user.has_write_access)

    def _realpath(self, path, permission_check):
        path = self.canonicalize(path).lstrip('/')
        if not permission_check(path):
            raise PermissionDenied()
        return os.path.join(self.root, path)

    @clean_response
    @log_it
    def open(self, path, flags, attr):
        # We ignore `attr` -- we choose the permissions
        read_only = (flags == os.O_RDONLY)
        if read_only:
            realpath = self.realpath_for_read(path)
        else:
            realpath = self.realpath_for_write(path)
        fd = os.open(realpath, flags, self.FILE_MODE)
        fileobj = os.fdopen(fd, self.flags_to_string(flags), self.FILE_MODE)
        handle = SFTPFileHandle(paramiko.SFTPHandle(flags))
        handle.readfile = fileobj
        if not read_only:
            handle.writefile = fileobj
        return handle

    @clean_response
    @log_it
    def list_folder(self, path):
        realpath = self.realpath_for_read(path)
        return [self.sftp_attributes(os.path.join(realpath, filename))
                    for filename in os.listdir(realpath)]

    @clean_response
    @log_it
    def stat(self, path):
        return self.sftp_attributes(self.realpath_for_read(path), follow_links=True)

    @clean_response
    def lstat(self, path):
        return self.sftp_attributes(self.realpath_for_read(path))

    @clean_response
    @log_it
    def remove(self, path):
        os.unlink(self.realpath_for_write(path))

    @clean_response
    @log_it
    def rename(self, oldpath, newpath):
        realpath_old = self.realpath_for_write(oldpath)
        realpath_new = self.realpath_for_write(newpath)
        #  renames must be non-destructive
        if os.path.exists(realpath_new):
            raise OSError(errno.EEXIST)
        os.rename(realpath_old, realpath_new)

    @clean_response
    @log_it
    def mkdir(self, path, attr):
        # We ignore `attr` -- we choose the permissions
        os.mkdir(self.realpath_for_write(path), self.DIRECTORY_MODE)

    @clean_response
    @log_it
    def rmdir(self, path):
        os.rmdir(self.realpath_for_write(path))

    @clean_response
    @log_it
    def chattr(self, path, attr):
        # Run but don't do anything
        pass

    @clean_response
    @log_it
    def readlink(self, path):
        # We only allow `readlink` on relative links that stay within the
        # shared root directory
        realpath = self.realpath_for_read(path)
        target = os.readlink(realpath)
        if os.path.isabs(target):
            return paramiko.SFTP_OP_UNSUPPORTED
        target_abs = os.path.normpath(os.path.join(
            os.path.dirname(realpath), target))
        if not target_abs.startswith(self.root + '/'):
            return paramiko.SFTP_OP_UNSUPPORTED
        return target

    def sftp_attributes(self, filepath, follow_links=False):
        filename = os.path.basename(filepath)
        stat = os.stat if follow_links else os.lstat
        return paramiko.SFTPAttributes.from_stat(
            stat(filepath), filename=filename)


    def flags_to_string(self, flags):
        if flags & os.O_WRONLY:
            if flags & os.O_APPEND:
                mode = 'a'
            else:
                mode = 'w'
        elif flags & os.O_RDWR:
            if flags & os.O_APPEND:
                mode = 'a+'
            else:
                mode = 'r+'
        else:
            mode = 'r'
        # Force binary mode
        mode += 'b'
        return mode
