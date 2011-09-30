# -*- coding: utf-8 -*-
#from datetime import datetime
import hashlib
#from webob.exc import HTTPUnauthorized


_SECRET_KEY = hashlib.sha1('ip_local').hexdigest()


def auth(header, request, params):
    """ Token authentication

    The token is the SHA-1 sum of the concatenation of a secret key
    and the current date
    """
    # FIXME : It doesn't work yet
    #if header != hashlib.sha1(_SECRET_KEY+datetime.now()
    # .strftime('%Y-%m-%d %H')).hexdigest():
    #    raise HTTPUnauthorized()
    return True
