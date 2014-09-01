#!/usr/bin/env python3

import pgpkeyserv
from pgpkeyserv.packages import pgpparse

def main():

    s = pgpkeyserv.Server("http://pgp.mit.edu:80")
    k = s.search("0x7A35090F")

main()
