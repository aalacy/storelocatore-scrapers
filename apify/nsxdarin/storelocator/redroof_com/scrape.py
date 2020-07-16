import csv
import requests # ignore_check
import os
import re
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import ConnectionError
from sgrequests import SgRequests
import collections


def override_retries():
    # monkey patch sgrequests in order to set max retries
    def new_init(self):
        requests.packages.urllib3.disable_warnings()
        self.session = self.requests_retry_session(retries=0)

    SgRequests.__init__ = new_init


override_retries()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
}

re_get_json = re.compile(
    'Utilities\.SDL\.Add\("ServicePropertyDetails", (.+?)\);')


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def get_json_data(html):
    match = re.search(re_get_json, html)
    json_text = match.group(1)
    return json.loads(json_text)


def get_sitemap(attempts=1):
    if attempts > 10:
        print("Couldn't get sitemap after 10 attempts")
        raise SystemExit
    try:
        session = SgRequests()
        url = 'https://www.redroof.com/sitemap.xml'
        r = session.get(url, headers=headers)
        return r
    except (ConnectionError, Exception) as ex:
        print("Exception getting sitemap", ex)
        return get_sitemap(attempts=attempts+1)


def fetch_data():
    locs = []
    r = get_sitemap()
    for line in r.iter_lines(decode_unicode=True):
        if 'https://www.redroof.com/property/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    # print('Found %s Locations.' % str(len(locs)))
    q = collections.deque(locs)
    attempts = {}
    while q:
        loc = q.popleft()
        if '-CA/' in loc:
            country = 'CA'
        else:
            country = 'US'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        website = 'redroof.com'
        typ = ''
        lat = ''
        lng = ''
        hours = '<MISSING>'
        store = loc.rsplit('/', 1)[1]
        r2 = None
        try:
            session = SgRequests()
            # print(loc)
            r2 = session.get(loc, headers=headers)
        except (ConnectionError, Exception) as ex:
            print('Failed to connect to ' + loc)
            print("Exception: ", ex)
            if attempts.get(loc, 0) >= 3:
                print('giving up on ' + loc)
            else:
                q.append(loc)
                attempts[loc] = attempts.get(loc, 0) + 1
                print('attempts: ' + str(attempts[loc]))
            continue

        data = get_json_data(r2.text)

        name = data["Description"]
        add = data["Street1"] + (", " + data["Street2"]
                                 if data["Street2"] else "")
        city = data["City"]
        state = data["State"]
        zc = data["PostalCode"]
        phone = data["PhoneNumber"]
        typ = data["PropertyType"]
        lat = data["Latitude"]
        lng = data["Longitude"]

        location = [website, loc, name, add, city, state,
                    zc, country, store, phone, typ, lat, lng, hours]
        location = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in location]
        # print(location)
        # print('---------')
        yield location


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
