# -*- coding: utf-8 -*-
import json
import os

from webob.exc import HTTPServiceUnavailable, HTTPNotImplemented

# Use GeoIP (C/Python implementation) if available, then fallback to
# pygeoip (pure Python implementation)
try:
    import GeoIP as geoip

    # Monkey patch for compatibility with pygeoip
    geoip.GeoIP = lambda filename: geoip.open(filename, geoip.GEOIP_STANDARD)
except ImportError:
    try:
        import pygeoip as geoip
    except ImportError:
        # Neither GeoIP/pygeoip installed, display a clean error
        raise ImportError(
                "Unable to find a Python GeoIP module. Please install GeoIP ("
                "http://www.maxmind.com/app/python) or pygeoip ("
                "http://code.google.com/p/pygeoip/).")


_GEOLITE_CITIES = 'GeoLiteCity.dat'


def localised(globs, request):
    """ Returns information about the ip_address
    If GeoLite Cities is not installed, raise an error
    """
    if os.path.isfile(_GEOLITE_CITIES):
        gi = geoip.GeoIP(_GEOLITE_CITIES)
        try:
            record = gi.record_by_addr(request.match['ip_address'])
        except geoip.GeoIPError:
            raise HTTPNotImplemented('You can only parse IPv4 addresses')

        if record:
            record = dict(record)

            for key in record.keys():
                if hasattr(record[key], 'decode'):
                    record[key] = record[key].decode(
                                'ISO-8859-1').encode('utf-8')

            return json.dumps(record)
        else:
            return json.dumps({})
    else:
        raise HTTPServiceUnavailable('You must install GeoLite Cities '
                                     ': http://www.maxmind.com/app'
                                     '/geolitecountry')
