#!/usr/bin/env python3
# exception.py

class SchemeNotProvided(Exception):

    def __str__(self):
        return "No scheme was provided"


class SchemeNotAllowed(Exception):

    def __init__(self, url):
        self.url = url

    def __str__(self):
        return "%s is not a valid scheme" % self.url


class InvalidKeyID(Exception):

    def __init__(self, keyid):
        self.keyid = keyid

    def __str__(self):
        return "%s is not a valid key ID" % self.keyid
