import urllib2
import time
import os
import re
import csv
import requests

path = '.'  ### this is a relative path for where the output file will be put

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
session = requests.Session()

header = 'locator_domain,location_name,street_address,city,state,zip,country_code,store_number,phone,location_type,naics_code,latitude,longitude,hours_of_operation\n'
with open("%s/Marriott.csv" % path, "wb") as out_file:
            out_file.write(header)

hotels = []

url = 'https://www.marriott.com/sitemap.us.hws.1.xml'
r = session.get(url, headers=headers, stream=True)
for line in r.iter_lines():
    if '<loc>https://www.marriott.com/hotels/travel/' in line:
        hurl = line.split('>')[1].split('<')[0]
        hotels.append(hurl)

print('Found %s Hotels...' % len(hotels))

count = 0

for hotel in hotels:
    count = count + 1
    print('Pulling Hotel %s of %s...' % (count, len(hotels)))
    r = session.get(hotel, headers=headers, stream=True)
    hid = hotel.split('/travel/')[1].split('-')[0]
    domain = 'https://www.marriott.com'
    brand = ''
    name = ''
    lat = ''
    lng = ''
    add = ''
    city = ''
    zc = ''
    state = ''
    country = ''
    phone = ''
    for line in r.iter_lines():
        if 'prop_address_city": "' in line:
            city = line.split('prop_address_city": "')[1].split('"')[0]
        if '"prop_address_state_name": "' in line:
            state = line.split('"prop_address_state_name": "')[1].split('"')[0]
        if '"prop_brand_name": "' in line:
            brand = line.split('"prop_brand_name": "')[1].split('"')[0].replace('"',"'").replace(':','-')
        if '"prop_name": "' in line:
            name = line.split('"prop_name": "')[1].split('"')[0]
        if '"prop_address_lat_long": "' in line:
            lat = line.split('"prop_address_lat_long": "')[1].split(',')[0]
            lng = line.split('"prop_address_lat_long": "')[1].split(',')[1].split('"')[0]
        if 'itemprop="streetAddress">' in line:
            add = line.split('itemprop="streetAddress">')[1].split('<')[0]
        if 'itemprop="addressLocality">' in line and city == '':
            city = line.split('itemprop="addressLocality">')[1].split('<')[0]
        if 'itemprop="postalCode">' in line:
            zc = line.split('itemprop="postalCode">')[1].split('<')[0].strip()
        if 'itemprop="addressRegion">' in line and state == '':
            state = line.split('itemprop="addressRegion">')[1].split('<')[0]
        if 'itemprop="addressCountry">' in line:
            country = line.split('itemprop="addressCountry">')[1].split('<')[0]
        if '<a href="tel:' in line:
            phone = line.split('<a href="tel:')[1].split('"')[0]
    if country == 'USA' or country == 'Canada':
        if country == 'USA':
            country = 'US'
            if '-' in zc:
                zc = zc.split('-')[0]
        if country == 'Canada':
            country = 'CA'
            if 'St. John' in city:
                state = 'Newfoundland'
        info = '"' + domain + '","' + name + '","' + add + '","' + city + '","' + state + '","' + zc + '","' + country
        info = info + '","' + hid + '","' + phone + '","' + brand + '","","' + lat + '","' + lng + '",""'
        info = info.replace('&apos;',"'").replace('&amp;','&').replace('&#xE9;','e').replace('&#xE8;','e').replace('&#x2019;',"'").replace('&#xF1;','n')
        with open("%s/Marriott.csv" % path, "ab") as out_file:
            out_file.write(info + '\n')
