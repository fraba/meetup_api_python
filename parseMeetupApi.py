#!/usr/bin/env python

## Copyright 2014 Francesco Bailo

## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

# parseMeetupApi.py

# Call it from console passing database filename: python parseMeetupApi.py <database> <API key>

import sqlite3
import sys
import os
import json
import requests
import datetime

# Receive the arguments from bash
database = sys.argv[1] + '.sqlite'
api_key = sys.argv[2]

## Functions

def main (api_key, database):

    # Open database connection
    conn = sqlite3.connect(database)
    conn.text_factory = str
    cursor = conn.cursor()

    # Uncomment to find/add new groups
    # findGroups(api_key, cursor)
    # conn.commit()
    
    # requestMembers(api_key, cursor)
    # conn.commit()
    requestEvents(api_key, cursor)
    conn.commit()
    # requestRsvps(api_key, cursor)
    # conn.commit()

def convertToTimestamp (ms):

    s = ms / 1000.0
    return datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S')
    

    
def findGroups (api_key, cursor):

    url = composeApiRequest('find/groups') + "&key=" + api_key + "&offset="
    offset = 0
    
    while True:
        response = requests.get(url + str(offset)).json()
        
        if any(response):
            print offset
            parseGroups(response, cursor)
            offset += 1

        else:
            print('No more pages')
            break

        
def requestMembers (api_key, cursor):

    # Retrive group_id from database
    # cursor.execute("SELECT group_id FROM [group]")
    cursor.execute("SELECT [group].group_id FROM [group] LEFT OUTER JOIN group_member ON [group].group_id = group_member.group_id WHERE group_member.group_id IS NULL")

    for (group_id,) in cursor.fetchall():

        url = composeApiRequest("members") + "group_id=" + group_id + \
              "&key=" + api_key
        print "Requesting members of group " + group_id + "..."
        response = requests.get(url).json()
        if 'results' in response:
            print "API returned the first page of members, parsing it..."
            parseMembers(response['results'], group_id, cursor)

            # Check for additional pages
            while True:
                print "Checking if there is another page of members..."
                if response['meta']['next']:
                    print "There is an additional page, parsing it..."
                    response = requests.get(response['meta']['next']).json()
                    if 'results' in response:
                        parseMembers(response['results'], group_id, cursor)
                else:
                    print "There is no more page of members, moving to next group..."
                    break

        else:
            print "Something went wrong: " + response['problem']
            break

def requestEvents (api_key, cursor):

    # Retrive group_id from database
    # cursor.execute("SELECT group_id FROM [group]")
    cursor.execute("SELECT [group].group_id FROM [group] LEFT OUTER JOIN event ON [group].group_id = event.group_id WHERE event.group_id IS NULL")

    for (group_id,) in cursor.fetchall():

        url = composeApiRequest("events") + "group_id=" + group_id + \
              "&status=past" + "&key=" + api_key
        print "Requesting events of group " + group_id + "..."
        try:
            response = requests.get(url).json()
            if 'results' in response:
                print "API returned the first page of events, parsing it..."
                parseEvents(response['results'], cursor)

                # Check for additional pages
                while True:
                    print "Checking if there is another page of events..."
                    if response['meta']['next']:
                        print "There is an additional page, parsing it..."
                        response = requests.get(response['meta']['next']).json()
                        if 'results' in response:
                            parseEvents(response['results'], cursor)
                    else:
                        print "There is no more page of events, moving to next group..."
                        break

            else:
                print "Something went wrong: " + response['problem']
                break
        except:
            pass

        
def requestRsvps (api_key, cursor):

    # Retrive group_id from database
    cursor.execute("SELECT event_id FROM event")

    for (event_id,) in cursor.fetchall():

        url = composeApiRequest("rsvps") + "event_id=" + event_id + \
              "&key=" + api_key
        print "Requesting RSVPS of event " + event_id + "..."
        response = requests.get(url).json()
        if 'results' in response:
            print "API returned the first page of RSVPS, parsing it..."
            parseRsvps(response['results'], cursor)

            # Check for additional pages
            while True:
                print "Checking if there is another page of RSVPS..."
                if response['meta']['next']:
                    print "There is an additional page, parsing it..."
                    response = requests.get(response['meta']['next']).json()
                    if 'results' in response:
                        parseRsvps(response['results'], cursor)
                else:
                    print "There is no more page of RSVPS, moving to next event..."
                    break

        else:
            print "Something went wrong: " + response['problem']
            break
        
        
def composeApiRequest(request_type):

    base_url = "https://api.meetup.com/"

    if request_type == "find/groups":
        # Define search terms
        category = "13" # "Movements & Politics"
        country = "IT"
        radius = "global"
        text = "beppe+grillo"
        page = "200"
        url = base_url + request_type + "?" + "category=" + category + \
              "&country=" + country + "&radius=" + radius + "&text=" + text + \
              "&page=" + page
        return url

    else:
        url = base_url + "2/" + request_type + "?"
        return url
                
def parseGroups (response, cursor):

    for group_item in response:

        # Parse group
        group = {}
        group['group_id'] = group_item.get('id')
        group['category'] = group_item['category'].get('name')
        group['city'] = group_item.get('city')
        group['country'] = group_item.get('country')
        group['created'] = group_item.get('created')
        group['description'] = group_item.get('description')
        group['join_mode'] = group_item.get('join_mode')
        group['lat'] = group_item.get('lat')
        group['link'] = group_item.get('link')
        group['lon'] = group_item.get('lon')
        group['members'] = group_item.get('members')
        group['name'] = group_item.get('name')
        group['organizer'] = group_item['organizer'].get('id')
        group['state'] = group_item.get('state')
        group['timezone'] = group_item.get('timezone')
        group['urlname'] = group_item.get('urlname')
        group['visibility'] = group_item.get('visibility')
        group['who'] = group_item.get('who')

        enterGroup(group, cursor)

    return

def parseMembers (results, group_id, cursor):

    for member_item in results:

        # Parse member
        member = {}
        member['member_id'] = member_item.get('id')
        member['bio'] = member_item.get('bio')
        if 'birthday' in member_item:
            member['birthday'] = member_item['birthday'].get('year')
        else:
            member['birthday'] = None
        member['city'] = member_item.get('city')
        member['country'] = member_item.get('country')
        member['gender'] = member_item.get('gender')
        member['joined'] = member_item.get('joined')
        member['lang'] = member_item.get('lang')
        member['lat'] = member_item.get('lat')
        member['link'] = member_item.get('link')
        member['lon'] = member_item.get('lon')
        member['name'] = member_item.get('name')
        if 'facebook' in member_item['other_services']:
            member['facebook'] = member_item['other_services']['facebook'].get('identifier')
        else:
            member['facebook'] = None
        if 'twitter' in member_item['other_services']:
            member['twitter'] = member_item['other_services']['twitter'].get('identifier')
        else:
            member['twitter'] = None
        if 'flickr' in member_item['other_services']:
            member['flickr'] = member_item['other_services']['flickr'].get('identifier')
        else:
            member['flickr'] = None
        if 'tumblr' in member_item['other_services']:
            member['tumblr'] = member_item['other_services']['tumblr'].get('identifier')
        else:
            member['tumblr'] = None
        if 'linkedin' in member_item['other_services']:
            member['linkedin'] = member_item['other_services']['linkedin'].get('identifier')
        else:
            member['linkedin'] = None

        enterMember(member, cursor)

        # Create and fill group_member pair
        group_member = {}
        group_member['group_id'] = group_id
        group_member['member_id'] = member['member_id']

        enterGroupMember(group_member, cursor)

        # Get all topics
        for topic_item in member_item['topics']:

            topic = {}
            topic['topic_id'] = topic_item.get('id')
            topic['name'] = topic_item.get('name')
            topic['urlkey'] = topic_item.get('urlkey')

            enterTopic(topic, cursor)

            # Create and enter topic member pair 
            topic_member = {}
            topic_member['topic_id'] = topic['topic_id']
            topic_member['member_id'] = member['member_id']

            enterTopicMember(topic_member, cursor)

    return

def parseEvents (results, cursor):

    for event_item in results:

        # Parse event
        event = {}
        event['event_id'] = event_item.get('id')
        event['created'] = event_item.get('created')
        event['description'] = event_item.get('description')
        event['event_url'] = event_item.get('event_url')
        event['group_id'] = event_item['group'].get('id')
        event['headcount'] = event_item.get('headcount')
        event['maybe_rsvp_count'] = event_item.get('maybe_rsvp_count')
        event['name'] = event_item.get('name')
        event['rating_average'] = event_item['rating'].get('average')
        event['rating_count'] = event_item['rating'].get('count')
        event['status'] = event_item.get('status')
        event['time'] = event_item.get('time')
        event['updated'] = event_item.get('updated')
        event['utc_offset'] = event_item.get('utc_offset')
        if 'venue' in event_item:
            event['venue'] = event_item['venue'].get('id')
        else:
            event['venue'] = None
        event['visibility'] = event_item.get('visibility')
        event['waitlist_count'] = event_item.get('waitlist_count')
        event['yes_rsvp_count'] = event_item.get('yes_rsvp_count')

        enterEvent(event, cursor)

        if 'venue' in event_item:
            # Parse venue
            venue = {}
            venue['venue_id'] =  event_item['venue'].get('id')
            venue['address_1'] =  event_item['venue'].get('address_1')
            venue['address_2'] =  event_item['venue'].get('address_2')
            venue['address_3'] =  event_item['venue'].get('address_3')
            venue['city'] =  event_item['venue'].get('city')
            venue['country'] =  event_item['venue'].get('country')
            venue['lat'] =  event_item['venue'].get('lat')
            venue['lon'] =  event_item['venue'].get('lon')
            venue['name'] =  event_item['venue'].get('name')

            enterVenue(venue, cursor)
        
    return 


def parseRsvps (results, cursor):

    for rsvps_item in results:

        rsvps = {}
        rsvps['rsvps_id'] = rsvps_item.get('rsvp_id')
        rsvps['member_id'] = rsvps_item['member'].get('member_id')
        rsvps['event_id'] = rsvps_item['event'].get('id')
        rsvps['created'] = rsvps_item.get('created')

        enterRsvps(rsvps, cursor)

    return

        
def enterGroup (object, cursor):

    cursor.execute("INSERT OR IGNORE INTO [group] (group_id, category, city, country, created, description, join_mode, lat, link, lon, members, name, organizer, state, timezone, urlname, visibility, who) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (object['group_id'], object['category'], object['city'], object['country'], convertToTimestamp(object['created']), object['description'], object['join_mode'], object['lat'], object['link'], object['lon'], object['members'], object['name'], object['organizer'], object['state'], object['timezone'], object['urlname'], object['visibility'], object['who']))    

    return


def enterMember (object, cursor):

    cursor.execute("INSERT OR IGNORE INTO member (member_id, bio, birthday, city, country, gender, joined, lang, lat, link, lon, name, facebook, twitter, flickr, tumblr, linkedin) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (object['member_id'], object['bio'], object['birthday'], object['city'], object['country'], object['gender'], convertToTimestamp(object['joined']), object['lang'], object['lat'], object['link'], object['lon'], object['name'], object['facebook'], object['twitter'], object['flickr'], object['tumblr'], object['linkedin']))    

    return


def enterGroupMember (object, cursor):

    cursor.execute("INSERT OR IGNORE INTO group_member (member_id, group_id) VALUES (?, ?)", (object['member_id'], object['group_id']))    

    return


def enterTopic (object, cursor):

    cursor.execute("INSERT OR IGNORE INTO topic (topic_id, name, urlkey) VALUES (?, ?, ?)", (object['topic_id'], object['name'], object['urlkey']))    

    return


def enterTopicMember (object, cursor):

    cursor.execute("INSERT OR IGNORE INTO topic_member (topic_id, member_id) VALUES (?, ?)", (object['topic_id'], object['member_id']))    

    return

def enterEvent (object, cursor):

    cursor.execute("INSERT OR IGNORE INTO event (event_id, created, description, event_url, group_id, headcount, maybe_rsvp_count, name, rating_average, rating_count, status, time, updated, utc_offset, venue, visibility, waitlist_count, yes_rsvp_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (object['event_id'], convertToTimestamp(object['created']), object['description'], object['event_url'], object['group_id'], object['headcount'], object['maybe_rsvp_count'], object['name'], object['rating_average'], object['rating_count'], object['status'], convertToTimestamp(object['time']), convertToTimestamp(object['updated']), object['utc_offset'], object['venue'], object['visibility'], object['waitlist_count'], object['yes_rsvp_count']))    

    return


def enterVenue (object, cursor):

    cursor.execute("INSERT OR IGNORE INTO venue (venue_id, address_1, address_2, address_3, city, country, lat, lon, name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (object['venue_id'], object['address_1'], object['address_2'], object['address_3'], object['city'], object['country'], object['lat'], object['lon'], object['name']))    

    return


def enterRsvps (object, cursor):

    cursor.execute("INSERT OR IGNORE INTO rsvps (rsvps_id, member_id, event_id, created) VALUES (?, ?, ?, ?)", (object['rsvps_id'], object['member_id'], object['event_id'], convertToTimestamp(object['created'])))    

    return


# Execute the program
main(api_key, database)
