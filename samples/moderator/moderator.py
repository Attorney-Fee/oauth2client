#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Buzz.

Command-line application that retrieves the users
latest content and then adds a new entry.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


from apiclient.discovery import build
from apiclient.oauth import FlowThreeLegged
from apiclient.ext.authtools import run
from apiclient.ext.file import Storage
from apiclient.oauth import CredentialsInvalidError

import httplib2

# Uncomment to get detailed logging
# httplib2.debuglevel = 4


def main():
  storage = Storage('moderator.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    moderator_discovery = build("moderator", "v1").auth_discovery()

    flow = FlowThreeLegged(moderator_discovery,
                           consumer_key='anonymous',
                           consumer_secret='anonymous',
                           user_agent='google-api-client-python-mdrtr-cmdline/1.0',
                           domain='anonymous',
                           scope='https://www.googleapis.com/auth/moderator',
                           #scope='tag:google.com,2010:auth/moderator',
                           xoauth_displayname='Google API Client Example App')

    credentials = run(flow, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  p = build("moderator", "v1", http=http)

  series_body = {
      "data": {
        "description": "Share and rank tips for eating healthy and cheap!",
        "name": "Eating Healthy & Cheap",
        "videoSubmissionAllowed": False
        }
      }
  try:
    series = p.series().insert(body=series_body).execute()
    print "Created a new series"

    topic_body = {
        "data": {
          "description": "Share your ideas on eating healthy!",
          "name": "Ideas",
          "presenter": "liz"
          }
        }
    topic = p.topics().insert(seriesId=series['id']['seriesId'],
                              body=topic_body).execute()
    print "Created a new topic"

    submission_body = {
        "data": {
          "attachmentUrl": "http://www.youtube.com/watch?v=1a1wyc5Xxpg",
          "attribution": {
            "displayName": "Bashan",
            "location": "Bainbridge Island, WA"
            },
          "text": "Charlie Ayers @ Google"
          }
        }
    submission = p.submissions().insert(seriesId=topic['id']['seriesId'],
        topicId=topic['id']['topicId'], body=submission_body).execute()
    print "Inserted a new submisson on the topic"

    vote_body = {
        "data": {
          "vote": "PLUS"
          }
        }
    p.votes().insert(seriesId=topic['id']['seriesId'],
                     submissionId=submission['id']['submissionId'],
                     body=vote_body)
    print "Voted on the submission"
  except CredentialsInvalidError:
    print 'Your credentials are no longer valid.'
    print 'Please re-run this application to re-authorize.'


if __name__ == '__main__':
  main()
