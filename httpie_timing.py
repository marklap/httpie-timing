"""
Plugin to produce timing statements on httpie output.

"""
from __future__ import print_function
import sys
import time
from collections import defaultdict

from httpie.plugins.base import TransportPlugin, FormatterPlugin
from requests.adapters import HTTPAdapter, DEFAULT_POOLBLOCK
from requests.packages.urllib3.poolmanager import PoolManager, SSL_KEYWORDS
from requests.packages.urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from requests.packages.urllib3.connection import HTTPConnection, HTTPSConnection, port_by_scheme
from requests.packages.urllib3.util import parse_url


__version__ = (0, 0, 1)
VERSION = '.'.join(map(str, __version__))
CONFIG_KEY = 'httpie-timing'
OUTPUT_KEY = 'output'
OUTPUTS = ['headers',]
DEFAULT_OUTPUT = OUTPUTS[0]

# for now we store timings in the module's globals
_httpie_timings = defaultdict(dict)

from pprint import pprint, pformat

class TimingHTTPConnection(HTTPConnection):

    def _new_conn(self):
        global _httpie_timings
        _httpie_timings['connection-start'] = time.time()
        conn = super(TimingHTTPConnection, self)._new_conn()
        _httpie_timings['connection-finish'] = time.time()
        _httpie_timings['connection-duration'] = _httpie_timings['connection-finish'] - _httpie_timings['connection-start']
        return conn


class TimingHTTPSConnection(TimingHTTPConnection, HTTPSConnection):
    pass


class TimingHTTPConnectionPool(HTTPConnectionPool):

    ConnectionCls = TimingHTTPConnection


class TimingHTTPSConnectionPool(HTTPSConnectionPool):

    ConnectionCls = TimingHTTPSConnection


class TimingPoolManager(PoolManager):

    def _new_pool(self, scheme, host, port):
        pool_cls = {
                    'http': TimingHTTPConnectionPool,
                    'https': TimingHTTPSConnectionPool,
                    }[scheme]
        kwargs = self.connection_pool_kw
        if scheme == 'http':
            kwargs = self.connection_pool_kw.copy()
            for kw in SSL_KEYWORDS:
                kwargs.pop(kw, None)

        return pool_cls(host, port, **kwargs)


class TimingHTTPAdapter(HTTPAdapter):

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        global _httpie_timings
        scheme, auth, host, port, path, query, fragment = parse_url(request.url)

        if port is None:
            port = port_by_scheme[scheme]

        _httpie_timings['request-start'] = time.time()
        response = super(TimingHTTPAdapter, self).send(request, stream, timeout, verify, cert, proxies)
        _httpie_timings['request-finish'] = time.time()
        _httpie_timings['request-duration'] = _httpie_timings['request-finish'] - _httpie_timings['request-start']

        return response


    def init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs):
        self._pool_connections = connections
        self._pool_maxsize = maxsize
        self._pool_block = block

        self.poolmanager = TimingPoolManager(num_pools=connections, maxsize=maxsize,
                                       block=block, strict=True, **pool_kwargs)


class TimingHTTPPlugin(TransportPlugin):

    prefix = 'http://'

    def get_adapter(self):
        return TimingHTTPAdapter()


class TimingHTTPSPlugin(TransportPlugin):

    prefix = 'https://'

    def get_adapter(self):
        return TimingHTTPAdapter()


class TimingFormatterPlugin(FormatterPlugin):

    def format_headers(self, headers):

        try:
            output_method = self.kwargs['env'].config[CONFIG_KEY][OUTPUT_KEY]
        except KeyError:
            output_method = DEFAULT_OUTPUT

        if output_method == 'headers':
            headers += '\nX-HTTPIE-TIMING-CONNECTION: {0}'.format(_httpie_timings['connection-duration'])
            headers += '\nX-HTTPIE-TIMING-REQUEST: {0}'.format(_httpie_timings['request-duration'])

        return headers
