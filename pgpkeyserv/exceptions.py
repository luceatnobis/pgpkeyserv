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

class NoKeyFound(Exception):

    def __init__(self, keyid):
        self.keyid = keyid

    def __str__(self):
        return "No keys for %s were found." % self.keyid


class InvalidResponse(Exception):

    def __init__(self, response):
        self.resp = response

    def __str__(self):
        return "Invalid response: %s" % self.resp


class TooManySearchResults(Exception):

    def __init__(self, count, limit):
        self.count = count
        self.limit = limit

    def __str__(self):
        return "Found %s results, limit is %s" % (self.count, self.limit)
