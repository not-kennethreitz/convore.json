# -*- coding: utf-8 -*-

import os
import json
from jinja2 import Template

from codecs import open
from datetime import datetime

# groups/{group-slug}/topics.json,{topic-slug}/messages.json

def mkdir_p(filename):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass

def get_users():
    with open('users.json') as f:
        users = json.loads(f.read())['users']

    users = sorted(users, key=lambda k: k['date_joined'])
    for i, message in enumerate(users):
        users[i]['date_joined'] = datetime.fromtimestamp(message['date_joined']).strftime('%c')
    return users

def get_groups(users):
    with open('groups.json') as f:
        groups = json.loads(f.read())

    groups = sorted(groups, key=lambda k: k['date_created'])

    for i, group in enumerate(groups):
        groups[i]['members'] = sorted(groups[i]['members'], key=lambda k: k['date_created'])
        groups[i]['user'] = users[group['creator_id']]

    return groups

def get_topics(group, users):
    with open('groups/{}/topics.json'.format(group)) as f:
        topics = json.loads(f.read())

    topics = sorted(topics, key=lambda k: k['date_created'])

    for i, topic in enumerate(topics):
        topics[i]['user'] = users[topic['creator_id']]

    return topics



def get_messages(group, topic, users):
    with open('groups/{}/{}/messages.json'.format(group, topic)) as f:
        messages = json.loads(f.read())

    messages = sorted(messages, key=lambda k: k['date_created'])

    for i, message in enumerate(messages):
        messages[i]['date_created'] = datetime.fromtimestamp(message['date_created']).strftime('%b %d %Y %H:%M')
        messages[i]['user'] = users[message['user_id']]

    return messages

GROUP_TEMPLATE = """
<link rel="stylesheet" href="/tufte.css"/>

<h1> <a href="/index.html">Convore</a> /
<a href="/groups.html">Groups</a> /
{{ name }}
</h1>

{% if user.name %}
Created by <a href="/users/{{ user.username }}.html">{{ user.name }}</a>.
{% else %}
Created by <a href="/users/{{ user.username }}.html">{{ user.username }}</a>.
{% endif %}



<h2>Group Topics</h2>

<ul>
{% for topic in topics %}
    <li><a href="/groups/{{ slug }}/{{ topic.slug }}.html">{{ topic.name }}</a></li>
{% endfor%}
</ul>

"""

def render_group(group, topics):

    filename = 'html/groups/{}.html'.format(group['slug'])
    mkdir_p(filename)

    template = Template(GROUP_TEMPLATE)
    html = template.render(topics=topics, **group)

    with open(filename, 'w', 'utf-8') as f:
        f.write(html)

TOPIC_TEMPLATE = """
<link rel="stylesheet" href="/tufte.css"/>

<h1> <a href="/index.html">Convore</a> /
<a href="/groups.html">Groups</a> /
<a href="/groups/{{ group.slug }}.html">{{ group.name }}</a>:
</h1>

<h2>{{ name }}</h2>

{% if user.name %}
<p>Created by <a href="/users/{{ user.username }}.html">{{ user.name }}</a>.</p>
{% else %}
<p>Created by <a href="/users/{{ user.username }}.html">{{ user.username }}</a>.</p>
{% endif %}

<h2>Topic Messages</h2>

{% for message in messages %}
    <h4><a href="/users/{{ message.user.username }}.html">{{ message.user.username }}</a> at {{ message.date_created }}</h4>

    {% if message.stars %}
        {{ "&#9733;" * message.stars|length }}
    {% endif %}

    <p>{{ message.message }}</p>
    <p>&nbsp;</p>
{% endfor%}

"""

def render_topic(group, topic, messages):


    filename = 'html/groups/{}/{}.html'.format(group['slug'], topic['slug'])
    mkdir_p(filename)

    template = Template(TOPIC_TEMPLATE)
    html = template.render(group=group, messages=messages, **topic)

    with open(filename, 'w', 'utf-8') as f:
        f.write(html)


USER_TEMPLATE = """
<link rel="stylesheet" href="/tufte.css"/>

<h1> <a href="/index.html">Convore</a> /
<a href="/users.html">Users</a> /
{{ user.username }}
</h1>

<h2>{{ user.name }}</h2>

<p>{{ user.bio }}</p>

{% if user.pic %}
    <img src="/avatars/{{ user.pic }}" />
{% endif %}

<p>

<table>
  <tr>
    <td>Location</td>
    <td>{{ user.location }}</td>
  </tr>
  <tr>
    <td>Web URL</td>
    <td><a href="{{ user.web }}">{{ user.web }}</a></td>
  </tr>
  <tr>
    <td>Date Joined</td>
    <td>{{ user.date_joined }}</td>
  </tr>
</table>

"""

def render_user(user):


    filename = 'html/users/{}.html'.format(user['username'])
    mkdir_p(filename)

    if user['pic']:
        user['pic'] = user['pic'].replace('/', '-')

    template = Template(USER_TEMPLATE)
    html = template.render(user=user)

    with open(filename, 'w', 'utf-8') as f:
        f.write(html)


USERS_TEMPLATE = """
<link rel="stylesheet" href="/tufte.css"/>

<h1> <a href="/index.html">Convore</a> /
Users
</h1>

{% for user in users %}


  {% if user.name %}
  <a href="/users/{{ user.username }}.html">

    {{ user.name }}
  {% else %}
  <a href="/users/{{ user.username }}.html">
    {{ user.username }}
  </a>
  {% endif %}
{% endfor%}

{% if next %}
<h1><a href="/users-{{ next }}.html">Next Page</a></h1>
{% endif %}

"""

def render_users(users, pagination=8000):

    i = 0
    page = 0

    while i < len(users):
        if page == 0:
            filename = 'html/users.html'
        else:
            filename = 'html/users-{}.html'.format(page)
        mkdir_p(filename)

        _users = users[pagination*page:pagination*page+pagination]
        i += len(_users)

        if len(_users) < pagination:
            next = False
        else:
            next = page + 1

        template = Template(USERS_TEMPLATE)
        html = template.render(users=_users, next=next)

        with open(filename, 'w', 'utf-8') as f:
            f.write(html)

        page += 1

GROUPS_TEMPLATE = """
<link rel="stylesheet" href="/tufte.css"/>

<h1> <a href="/index.html">Convore</a> /
Groups
</h1>

{% for group in groups %}

    <h3><a href="/groups/{{ group.slug }}.html">{{ group.name }}</a></h3>
    {{ group.members | count }} Members
    <p>{{ group.description }}</p>


{% endfor%}


{% if next %}
<h1><a href="/users-{{ next }}.html">Next Page</a></h1>
{% endif %}

"""

def render_groups(groups):

    filename = 'html/groups.html'
    mkdir_p(filename)

    template = Template(GROUPS_TEMPLATE)
    html = template.render(groups=groups)

    with open(filename, 'w', 'utf-8') as f:
        f.write(html)

message_count = 0
topic_count = 0

users = get_users()
user_lookup = {}

print 'Rendering user profiles...'
for user in users:
    user_lookup[user['id']] = user

    # render_user(user)

print 'Rendering user index...'
render_users(users)



groups = get_groups(users=user_lookup)

print 'Rendering groups...'
# render_groups(groups)

for group in groups:

    topics = get_topics(group['slug'], users=user_lookup)

    topic_count += len(topics)
    # render_group(group, topics)

    for topic in topics:
        messages = get_messages(group['slug'], topic['slug'], users=user_lookup)
        # render_topic(group, topic, messages)

        message_count += len(messages)

        print '{}: {} ({})'.format(group['slug'], topic['slug'], len(messages))

print 'messages: {}'.format(message_count)
print 'topics: {}'.format(topic_count)
print 'groups: {}'.format(len(groups))
print 'users: {}'.format(len(users))