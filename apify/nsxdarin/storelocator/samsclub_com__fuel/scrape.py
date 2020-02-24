import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.samsclub.com/sitemap_locators.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.samsclub.com/club/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    for loc in locs:
        Fuel = False
        #print('Pulling Location %s...' % loc)
        website = 'samsclub.com/fuel'
        typ = 'Gas'
        hours = ''
        name = ''
        country = 'US'
        city = ''
        add = ''
        zc = ''
        state = ''
        lat = ''
        lng = ''
        phone = ''
        store = loc.rsplit('/',1)[1]
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if ',"clubDetails":{"' in line2 and '"displayName":"Fuel Center"' in line2:
                Fuel = True
                cinfo = line2.split(',"clubDetails":{"')[1]
                name = cinfo.split('"name":"')[1].split('"')[0]
                zc = cinfo.split('"postalCode":"')[1].split('"')[0]
                try:
                    add = cinfo.split(',"address1":"')[1].split('"')[0]
                except:
                    add = ''
                try:
                    add = add + ' ' + cinfo.split('"address2":"')[1].split('"')[0]
                except:
                    pass
                city = cinfo.split('"city":"')[1].split('"')[0]
                state = cinfo.split('"state":"')[1].split('"')[0]
                phone = cinfo.split('"phone":"')[1].split('"')[0]
                lat = cinfo.split('"latitude":')[1].split(',')[0]
                lng = cinfo.split('"longitude":')[1].split('}')[0]
                fcinfo = cinfo.split('"displayName":"Fuel Center","operationalHours":')[1].split('}}},')[0]
                try:
                    sathrs = fcinfo.split('"saturdayHrs":{"')[1].split('":"')[1].split('"')[0] + '-' + cinfo.split('"saturdayHrs":{"')[1].split('"endHr":"')[1].split('"')[0]
                except:
                    sathrs = 'Closed'
                try:
                    sunhrs = fcinfo.split('"sundayHrs":{"')[1].split('":"')[1].split('"')[0] + '-' + cinfo.split('"sundayHrs":{"')[1].split('"endHr":"')[1].split('"')[0]
                except:
                    sunhrs = 'Closed'
                mfhrs = fcinfo.split('"monToFriHrs":{"')[1].split('":"')[1].split('"')[0] + '-' + cinfo.split('"monToFriHrs":{"')[1].split('"endHr":"')[1].split('"')[0]
                hours = 'M-F: ' + mfhrs + '; Sat: ' + sathrs + '; Sun: ' + sunhrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if Fuel is True and add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
