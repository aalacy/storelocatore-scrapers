import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.bpgroupusa.com/OurLocations.html'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    locs = []
    LFound = True
    LocFound = False
    website = 'bpgroupusa.com'
    name = '<MISSING>'
    add = '<MISSING>'
    city = '<MISSING>'
    state = '<MISSING>'
    zc = '<MISSING>'
    phone = '<MISSING>'
    hours = '<MISSING>'
    country = 'US'
    typ = 'Restaurant'
    store = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if 'id="canada">' in line:
            country = 'CA'
        if '<div class="row ourlocations-title" id="china">' in line:
            LFound = False 
        if '<div class="row ourlocations-title" id="japan">' in line:
            LFound = False  
        if LFound and '<div class="row ourlocations-row">' in line and '<!--' not in line:
            LocFound = True
        if '<!--' in line and '-->' not in line:
            LocFound = False
            next(lines)
            next(lines)
        if LocFound and '<p><span>' in line:
            LocFound = False
            hours = line.split('<p><span>')[1].split('<')[0]
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if LocFound and '<div class="ourlocations-box">' in line:
            name = next(lines).split('>')[1].split('<')[0]
            addline = next(lines)
            if '<p>' not in addline:
                addline = next(lines)
            add = addline.split('>')[1].split('<')[0]
            csz = next(lines)
            city = csz.split(',')[0]
            state = csz.split(',')[1].strip().split(' ',1)[0].replace('.','')
            zc = csz.split(',')[1].strip().split(' ',1)[1].split('<')[0].replace('OJ8','0J8')
        if '<li><a href="callto:' in line:
            phone = line.split('<li><a href="callto:')[1].split('"')[0]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
