# -*- coding: utf-8 -*-

import json
import requests


s = requests.session()

with open('users.json', 'r') as f:
    users_dump = json.loads(f.read())

# print len(users_dump['users'])

avatars = []

def get_avatars():

    for user in users_dump['users']:
        avatar = user['pic']

        if avatar:
            yield avatar

for avatar in get_avatars():
    url ='https://convore2.s3.amazonaws.com/{0}'.format(avatar)
    print avatar
    r = s.get(url=url, prefetch=True)

    with open(avatar.replace('/', '-'), 'wb') as f:
        f.write(r.content)
