#!/usr/bin/env python3
# server.py

import socket

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen

from pgpkeyserv import exception
from pgpkeyserv.packages.socks import socks

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket


class Server:
    """
    This is a class describing a pgp key server. It provides methods to search
    for a key on a keyserver.
    """

    def __init__(self, server="https://pgp.mit.edu", tor=None):
        allowed_schemes = ("http", "https", "hkp", "hkps")
        scheme_translation = {"hkp": "http", "hkps": "https"}

        self.abs_path = "pks/lookup"  # standard

        scheme, netloc, path = urlparse(server)[0:3]

        if not scheme:
            raise exception.SchemeNotProvided
        elif scheme not in allowed_schemes:
            raise exception.SchemeNotAllowed(scheme)

        scheme = scheme_translation.get(scheme, scheme)

        try:
            url, port = netloc.split(":")
        except ValueError:
            url, port = (netloc, 11371)

        self.keyserv_url = "%s://%s:%s" % (scheme, url, port)

    def search(self, keyid):
        """
        The search for keys on a pgp key server is specified in the hkp
        protocol, a draft for which is available at
        http://tools.ietf.org/id/draft-shaw-openpgp-hkp-00.txt

        The draft, however, is nothing more than that, and it explicitly states
        that use of this draft as material for reference is "inappropriate" and
        its validity only extends to 6 months beyond its creation .

        With all due respect paid, creating a draft in the year 2003 and not
        bothering to update it or marking it as obsolete and then calling its
        use as reference material "inappropriate" is inappropriate itself.

        Therefore, no fucks about appropriate-ness will be given at this point.

        The document describes two mandatory parameters, "search" and "op".
        As the purpose of this module is limited to retrieving a known key from
        a pgp server, we will confine ourselves to retrieving that key from the
        keyserver or failing in crippling agony.
        """
        keyid_prefix = "0x"
        if not keyid.startswith(keyid_prefix):
            raise exception.InvalidKeyID(keyid)

        search_params = {
            'options': 'mr',
            'op': 'search',
            'search': keyid,
        }

        param_str = urlencode(search_params)
        search_url = "http://pgp.mit.edu/pks/lookup?" + param_str
        mr_raw_keydata = urlopen(search_url).read().decode()
        res = self._parse_mr_res(mr_raw_keydata)

    def _parse_mr_res(self, res):
        print(dir(res))
