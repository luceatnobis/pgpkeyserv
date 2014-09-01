#!/usr/bin/env python3
# server.py

import sys
import socket

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen
from urllib.error import HTTPError

from pgpkeyserv import exceptions
from pgpkeyserv.packages.socks import socks

from pgpkeyserv.packages import pgpparse

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket


class Server:
    """
    This is a class describing a pgp key server. It provides methods to search
    for a key on a keyserver.
    """

    def __init__(self, server="http://pgp.mit.edu", tor=None):
        allowed_schemes = ("http", "https", "hkp", "hkps")
        scheme_translation = {"hkp": "http", "hkps": "https"}

        abs_path = "pks/lookup"  # standard

        scheme, netloc, path = urlparse(server)[0:3]

        if not scheme:
            raise exceptions.SchemeNotProvided
        elif scheme not in allowed_schemes:
            raise exceptions.SchemeNotAllowed(scheme)

        scheme = scheme_translation.get(scheme, scheme)

        try:
            url, port = netloc.split(":")
        except ValueError:
            url, port = (netloc, 11371)

        self.keyserv_url = "%s://%s:%s/%s" % (scheme, url, port, abs_path)

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
        if not keyid.startswith(keyid_prefix) or len(keyid) != 10:
            raise exceptions.InvalidKeyID(keyid)

        raw_keyid = keyid[2:]  # strips the 0x

        search_params = {
            'options': 'mr',
            'op': 'search',
            'search': keyid,
        }

        param_str = urlencode(search_params)
        search_url = self.keyserv_url + '?' + param_str

        try:  # urllib throws an exception upon 404. Fantastic.
            resp = urlopen(search_url)
        except HTTPError:
            return

        mr_raw_keydata = resp.read().decode()
        if not self._parse_search_overview(mr_raw_keydata, raw_keyid):
            return # TODO: think of something clever here

        key_params = {
                'options': 'mr',
                'op': 'get',
                'search': keyid
        }
        key_params_str = urlencode(key_params)
        key_url = self.keyserv_url + '?' + key_params_str

        # lets get the key
        try:  # if this goes wrong we have messed up. Horribly. Oh god.
            key = urlopen(key_url).read()
        except:
            print("Plot twist: everything you think you know is a lie.")
            raise Exception("End of the World in 3..2..1..")

        
        return pgpparse.key.Key(key)

    def _parse_search_overview(self, res, raw_keyid):
        lines = [x for x in res.splitlines() if x]

        try:
            info_line_data = lines.pop(0).split(':')
        except:
            raise(exceptions.InvalidResponse)

        response_version, result_count = [int(x) for x in info_line_data[1:3]]
        assert response_version == 1  # currently (2003) this is 1

        for line in lines:
            if "pub" not in line:
                continue
            try:
                _, srv_keyid, algo, keylen, _, _, flags = line.split(":")
            except ValueError:
                raise exceptions.InvalidResponse(line)
            if raw_keyid == srv_keyid:
                return True
        else:
            return None
