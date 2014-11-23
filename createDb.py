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

# createdb.py

# Call it from console passing database filename: python createdb.py filename

import sqlite3
import sys

# Receive the argument from bash
filename = sys.argv[1] + '.sqlite'
 
conn = sqlite3.connect(filename)
 
cursor = conn.cursor()
 
# Create database

# Create tables

cursor.execute("""
CREATE TABLE member (
    member_id CHAR PRIMARY KEY,
    bio TEXT,
    birthday CHAR,
    city TEXT,
    country CHAR,
    gender CHAR,
    joined DATETIME,
    lang CHAR,
    lat DOUBLE,
    link CHAR,
    lon DOUBLE,
    name TEXT,
    facebook CHAR,
    twitter CHAR,
    flickr CHAR,
    tumblr CHAR,
    linkedin CHAR,
    timestamp DATETIME DEFAULT ( CURRENT_TIMESTAMP )
    );
               """)

cursor.execute("""
CREATE TABLE [group] ( 
    group_id CHAR PRIMARY KEY,
    category TEXT,
    city CHAR,
    country CHAR,
    created DATETIME,
    description TEXT,
    join_mode CHAR,
    lat DOUBLE,
    link CHAR,
    lon DOUBLE,
    members INTEGER,
    name TEXT,
    organizer CHAR,
    state CHAR,
    timezone CHAR,
    urlname CHAR,
    visibility CHAR,
    who CHAR,
    timestamp DATETIME DEFAULT ( CURRENT_TIMESTAMP ),
    FOREIGN KEY(organizer) REFERENCES member(member_id)
    );
               """)

cursor.execute("""
CREATE TABLE group_member (
    group_member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id CHAR NOT NULL,
    member_id CHAR NOT NULL,
    timestamp DATETIME DEFAULT ( CURRENT_TIMESTAMP ),
    FOREIGN KEY(member_id) REFERENCES member(member_id),
    FOREIGN KEY(group_id) REFERENCES [group](group_id)
    );
               """)

cursor.execute("""
CREATE TABLE topic (
    topic_id CHAR PRIMARY KEY,
    name TEXT,
    urlkey CHAR,
    timestamp DATETIME DEFAULT ( CURRENT_TIMESTAMP )
    );
               """)

cursor.execute("""
CREATE TABLE topic_member (
    topic_member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id CHAR NOT NULL,
    member_id CHAR NOT NULL,
    timestamp DATETIME DEFAULT ( CURRENT_TIMESTAMP ),
    FOREIGN KEY(topic_id) REFERENCES topic(topic_id),
    FOREIGN KEY(member_id) REFERENCES member(member_id)
    );
               """)

cursor.execute("""
CREATE TABLE event (
    event_id CHAR PRIMARY KEY,
    created DATETIME,
    description TEXT,
    event_url TEXT,
    group_id CHAR NOT NULL,
    headcount INTGER,
    maybe_rsvp_count INTEGER,
    name TEXT,
    rating_average DOUBLE,
    rating_count INTEGER,
    status CHAR,
    time DATETIME,
    updated DATETIME,
    utc_offset INTEGER,
    venue CHAR,
    visibility CHAR,
    waitlist_count INTEGER,
    yes_rsvp_count INTEGER,
    timestamp DATETIME DEFAULT ( CURRENT_TIMESTAMP ),
    FOREIGN KEY(group_id) REFERENCES [group](group_id),
    FOREIGN KEY(venue) REFERENCES venue(venue_id)
    );
               """)

cursor.execute("""
CREATE TABLE venue (
    venue_id CHAR PRIMARY KEY,
    address_1 TEXT,
    address_2 TEXT,
    address_3 TEXT,
    city TEXT,
    country CHAR,
    lat DOUBLE,
    lon DOUBLE,
    name TEXT,
    timestamp DATETIME DEFAULT ( CURRENT_TIMESTAMP )
    );
               """)

cursor.execute("""
CREATE TABLE rsvps (
    rsvps_id INTEGER PRIMARY KEY,
    member_id CHAR NOT NULL,
    event_id CHAR NOT NULL,
    created DATETIME,
    timestamp DATETIME DEFAULT ( CURRENT_TIMESTAMP ),
    FOREIGN KEY(event_id) REFERENCES event(event_id),
    FOREIGN KEY(member_id) REFERENCES member(member_id)
    );
               """)

# Close connection
conn.commit()
