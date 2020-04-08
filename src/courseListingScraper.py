# Some inspiration taken from:
# https://github.com/aggie-coding-club/Rev-Registration/blob/0daa75507bc5377811d85bf16f5987c2be3a0a20/autoscheduler/scraper/banner_requests.py

import time
import random
import string

import requests
import json


SUBJECT = 'CSCE'
NUMBER = 465

SEMESTER = 'FALL'
YEAR = 2020

SEMESTERS = {
    'SPRING': '1',
    'SUMMER': '2',
    'FALL': '3',
}
TERM = str(YEAR) + SEMESTERS[SEMESTER] + '1',

BASE_URL = 'https://compassxe-ssb.tamu.edu/StudentRegistrationSsb/ssb/'
UNIQUE_SESSION_ID = ("".join(random.sample(string.ascii_lowercase, 5)) + str(int(time.time() * 1000)))


def create_session ():
    url = BASE_URL + 'term/search'

    params = {
        'mode': 'search',
        'dataType': 'json',
        'term': TERM,
        'uniqueSessionId': UNIQUE_SESSION_ID,
    }


    s = requests.Session()
    s.get(url, params=params)
    return s


def get_sections(session, num_subjects):
    url = BASE_URL + 'searchResults/searchResults'

    params = {
        'txt_subject': SUBJECT,
        'txt_courseNumber': NUMBER,
        'txt_term': TERM,
        'uniqueSessionId': UNIQUE_SESSION_ID,
        'pageMaxSize': num_subjects,
    }

    return session.get(url, params=params)




session = create_session()
sections = json.loads(get_sections(session, 3).text)

for section in sections['data']:
    print('\n\n')

    print(section['subject'], section['courseNumber'], '-', section['sequenceNumber'], '(' + section['meetingsFaculty'][0]['courseReferenceNumber'] + ')')
    print(section['courseTitle'])

    if section['seatsAvailable'] > 0: print('Seats available:\033[92m', section['seatsAvailable'], '\033[0m/', section['maximumEnrollment'])
    else: print('Seats available:\033[91m', section['seatsAvailable'], '\033[0m/', section['maximumEnrollment'])

    print('\nMeeting times:')
    for block in section['meetingsFaculty']:
        block = block['meetingTime']
        print (block['meetingTypeDescription'] + ':', block['building'], block['room'])
        print (block['beginTime'], '-', block['endTime'], '|', block['monday'], block['tuesday'], block['wednesday'], block['thursday'], block['friday'])
        print()