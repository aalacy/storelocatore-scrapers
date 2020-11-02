import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('brightpathkids_com')



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
    states = []
    url = 'https://brightpathkids.com/locations/'
    r = session.get(url, headers=headers, stream=True)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<div class="text-center">	<a href="https://brightpathkids.com/' in line:
            lurl = line.split('<div class="text-center">	<a href="')[1].split('"')[0]
            if '/locations/' in lurl:
                locs.append(lurl)
            else:
                states.append(lurl)
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers, stream=True)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<div class="text-center">	<a href="https://brightpathkids.com/locations/' in line2:
                locs.append(line2.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        website = 'brightpathkids.com'
        country = 'CA'
        typ = '<MISSING>'
        store = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        hours = '<MISSING>'
        r2 = session.get(loc, headers=headers, stream=True)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if 'var bhStoreLocatorLocation = {' in line2:
                store = line2.split('"id":"')[1].split('"')[0]
                add = line2.split('"address":"')[1].split('"')[0] + ' ' + line2.split('"address2":"')[1].split('"')[0]
                add = add.strip()
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"postal":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                country = line2.split('"country":"')[1].split('"')[0]
                lat = line2.split('"bh_storelocator_location_lat":"')[1].split('"')[0]
                lng = line2.split('"bh_storelocator_location_lng":"')[1].split('"')[0]
            if '{\\"textarea\\":\\"Hours:\\"},{\\"textarea\\":\\"' in line2:
                hours = line2.split('{\\"textarea\\":\\"Hours:\\"},{\\"textarea\\":\\"')[1].split('\\')[0]
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
