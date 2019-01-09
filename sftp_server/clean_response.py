import functools
import paramiko

def clean_response(fn):
    """
    Dectorator which converts exceptions into appropriate SFTP error codes,
    returns OK for functions which don't have a return value
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            value = fn(*args, **kwargs)
        except (OSError, IOError) as e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        except PermissionDenied:
            return paramiko.SFTP_PERMISSION_DENIED
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        if value is None:
            return paramiko.SFTP_OK
        else:
            return value
    return wrapper
