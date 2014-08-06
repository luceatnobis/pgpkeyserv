#!/usr/bin/env python3

import pgpkeyserv

def main():

    s = pgpkeyserv.Server("https://pgp.mit.edu:80")
    s.search("0x7A35090F")

main()
