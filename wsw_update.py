#!/usr/bin/python
#
# Example code derived from:
#
#    https://dev.twitter.com/docs/auth/oauth/single-user-with-examples#python
#    https://github.com/brosner/python-oauth2
#

import argos
import oauth2 as oauth
import json
import urllib
import ConfigParser
from os.path import expanduser
import argparse

def oauth_req(url, key, secret, http_method="GET", post_body=None, http_headers=None):
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth.Token(key=key, secret=secret)
    client = oauth.Client(consumer, token)

    resp, content = client.request(
        url,
        method=http_method,
        body=post_body,
        headers=http_headers,
        force_auth_header=True
        )
    return content
 

def update_status(status, api_key, api_secret):
    response_body = oauth_req(
        'https://api.twitter.com/1.1/statuses/update.json',
        api_key,
        api_secret,
        "POST",
        status
        )


def encode_status(status, lat, lon):
    twitter_update = { 'status' : status, 'lat' : lat, 'long' : lon, 'display_coordinates' : 'true' }
    return urllib.urlencode(twitter_update)


def get_last_location(platform_id):
    location = []
    date = None
    lat = None
    lon = None
    section_name = "platform_" + str(platform_id)
    if CONFIG.has_option(section_name, "date"):
        date = CONFIG.get(section_name, "date")
    if CONFIG.has_option(section_name, "lat"):
        lat = CONFIG.getfloat(section_name, "lat")
    if CONFIG.has_option(section_name, "lon"):
        lon = CONFIG.getfloat(section_name, "lon")
    location = [ date, lat, lon ]
    return location

def get_platform_name(platform_id):
    section_name = "platform_" + str(platform_id)
    name = CONFIG.get(section_name, "name")
    return name


def save_location(platform_id, date, lat, lon):
    section_name = "platform_" + str(platform_id)
    if not CONFIG.has_section(section_name):
        CONFIG.add_section(section_name)
    CONFIG.set(section_name, "date", date)
    CONFIG.set(section_name, "lat", lat)
    CONFIG.set(section_name, "lon", lon)    

    with open(CONFIG_FILE, 'wb') as configfile:
        CONFIG.write(configfile)

def get_platforms():
    argos_platforms = map(int, CONFIG.get("argos", "platforms").split(","))
    return argos_platforms


# --------------------------------------------------------------------------#

HOME = expanduser("~")
CONFIG_FILE=HOME + "/etc/wsw.conf"

CONFIG = ConfigParser.ConfigParser()
CONFIG.read(CONFIG_FILE)

CONSUMER_KEY = CONFIG.get("twitter", "consumer_key")
CONSUMER_SECRET = CONFIG.get("twitter", "consumer_secret")
API_KEY = CONFIG.get("twitter", "api_key")
API_SECRET = CONFIG.get("twitter", "api_secret")
argos_username = CONFIG.get("argos", "argos_username")
argos_password = CONFIG.get("argos", "argos_password")


parser = argparse.ArgumentParser()
parser.add_argument('platform_id', type=int)
args = parser.parse_args()

platform_id = args.platform_id

platform_name = get_platform_name(platform_id)
last_loc = get_last_location(platform_id)
current_loc = argos.get_current_location(argos_username, argos_password, platform_id)
current_lat = current_loc[1]
current_lon = current_loc[2]

section_name = "platform_" + str(platform_id)
twitter_status = CONFIG.get(section_name, "twitter_status")
twitter_request = encode_status (twitter_status, current_lat, current_lon)

if (cmp(last_loc, current_loc) == 0):
    print "[*] " + platform_name + " (" + str(platform_id) + "):\tno update"
else:
    print "[*] " + platform_name + " (" + str(platform_id) + "):\tlocation has changed"
    save_location(platform_id, current_loc[0], current_loc[1], current_loc[2])
    print "[+] last loc:\t" + str(last_loc)
    print "[+] current loc:\t" + str(current_loc)
    print twitter_status
    update_status (twitter_request, API_KEY, API_SECRET)

