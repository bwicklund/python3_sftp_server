import functools
import logging

def log_it(method):
    """
    Decorator logs method along with the current user
    """
    @functools.wraps(method)
    def method_wrapper(self, *args, **kwargs):
        string_args = ':'.join([arg for arg in args if isinstance(arg, str)])
        msg = '%s:%%s:%s:%s' % (method.__name__, self.user, string_args)
        try:
            response = method(self, *args, **kwargs)
        except Exception:
            logging.info((msg % 'error').encode('utf-8'))
            raise
        else:
            logging.info((msg % 'ok').encode('utf-8'))
        return response
    return method_wrapper
