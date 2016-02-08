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
    return users

def get_groups():
    with open('groups.json') as f:
        groups = json.loads(f.read())

    groups = sorted(groups, key=lambda k: k['date_created'])

    for i, group in enumerate(groups):
        groups[i]['members'] = sorted(groups[i]['members'], key=lambda k: k['date_created'])

    return groups

def get_topics(group):
    with open('groups/{}/topics.json'.format(group)) as f:
        topics = json.loads(f.read())

    return sorted(topics, key=lambda k: k['date_created'])

def get_messages(group, topic, users):
    with open('groups/{}/{}/messages.json'.format(group, topic)) as f:
        messages = json.loads(f.read())

    messages = sorted(messages, key=lambda k: k['date_created'])

    for i, message in enumerate(messages):
        messages[i]['date_created'] = datetime.fromtimestamp(message['date_created']).strftime('%H:%M %b %d %Y')
        messages[i]['user'] = users[message['user_id']]

    return messages

GROUP_TEMPLATE = """
<link rel="stylesheet" href="tufte.css"/>

<h1>Group: <a href="/groups/{{ slug }}.html">{{ name }}</a></h1>

<h2>Topics</h2>

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
<link rel="stylesheet" href="tufte.css"/>

<h1>Topic:
<a href="/groups.html">Groups</a> /
<a href="/groups/{{ group.slug }}.html">{{ group.name }}</a> /
<a href="/groups/{{ group.slug }}/{{ slug }}.html">{{ name }}</a>
</h1>

<h2>Messages</h2>

<ul>
{% for message in messages %}
  <li>
    <p><a href="/users/{{ message.user.username }}">{{ message.user.username }}</a> at {{ message.date_created }}

    {% if message.stars %}
        ({{ message.stars|length }} stars)
    {% endif %}
    </p>
    {{ message.message }}
  </li>
{% endfor%}
</ul>

"""

def render_topic(group, topic, messages):


    filename = 'html/groups/{}/{}.html'.format(group['slug'], topic['slug'])
    mkdir_p(filename)

    template = Template(TOPIC_TEMPLATE)
    html = template.render(group=group, messages=messages, **topic)

    with open(filename, 'w', 'utf-8') as f:
        f.write(html)


users = get_users()
user_lookup = {}
for user in users:
    user_lookup[user['id']] = user


for group in get_groups():

    topics = get_topics(group['slug'])

    render_group(group, topics)

    for topic in topics:
        messages = get_messages(group['slug'], topic['slug'], users=user_lookup)

        # for message
        # print messages[1]
        render_topic(group, topic, messages)


        print '{}: {} ({})'.format(group['slug'], topic['slug'], len(messages))
    break


# u'category', u'description', u'slug', u'creator_id', u'members', u'date_created', u'id', u'name']
# print groups

# {u'category': [{u'name': u'Technology', u'slug': u'technology-1'}], u'description': u'your favourite text editor', u'slug': u'chocolat', u'creator_id': 1855, u'members': [{u'admin': True, u'date_created': 1321999314.51599, u'user_id': 1855}], u'date_created': 1321999314.151898, u'id': 12280, u'name': u'Chocolat'}
