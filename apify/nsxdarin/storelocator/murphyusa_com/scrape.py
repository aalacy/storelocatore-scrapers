import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://service.murphydriverewards.com/api/store'
    payload = {"pageSize":1000,"range":5000,"latitude":30,"longitude":-85}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = 'murphyusa.com'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if ',"storeNumber":' in item:
                    typ = item.split('"chainName":"')[1].split('"')[0]
                    store = item.split(',"storeNumber":')[1].split(',')[0]
                    name = 'Store #' + store
                    phone = item.split('"phone":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    hours = 'Sun: ' + item.split('"sundayOpen":"')[1].split('"')[0] + '-' + item.split('"sundayClose":"')[1].split('"')[0]
                    hours = hours + '; Mon: ' + item.split('"mondayOpen":"')[1].split('"')[0] + '-' + item.split('"mondayClose":"')[1].split('"')[0]
                    hours = hours + '; Tue: ' + item.split('"tuesdayOpen":"')[1].split('"')[0] + '-' + item.split('"tuesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Wed: ' + item.split('"wednesdayOpen":"')[1].split('"')[0] + '-' + item.split('"wednesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Thu: ' + item.split('"thursdayOpen":"')[1].split('"')[0] + '-' + item.split('"thursdayClose":"')[1].split('"')[0]
                    hours = hours + '; Fri: ' + item.split('"fridayOpen":"')[1].split('"')[0] + '-' + item.split('"fridayClose":"')[1].split('"')[0]
                    hours = hours + '; Sat: ' + item.split('"saturdayOpen":"')[1].split('"')[0] + '-' + item.split('"saturdayClose":"')[1].split('"')[0]
                    loc = '<MISSING>'
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"pageSize":1000,"range":5000,"latitude":30,"longitude":-95}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = 'murphyusa.com'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if ',"storeNumber":' in item:
                    typ = item.split('"chainName":"')[1].split('"')[0]
                    store = item.split(',"storeNumber":')[1].split(',')[0]
                    name = 'Store #' + store
                    phone = item.split('"phone":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    hours = 'Sun: ' + item.split('"sundayOpen":"')[1].split('"')[0] + '-' + item.split('"sundayClose":"')[1].split('"')[0]
                    hours = hours + '; Mon: ' + item.split('"mondayOpen":"')[1].split('"')[0] + '-' + item.split('"mondayClose":"')[1].split('"')[0]
                    hours = hours + '; Tue: ' + item.split('"tuesdayOpen":"')[1].split('"')[0] + '-' + item.split('"tuesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Wed: ' + item.split('"wednesdayOpen":"')[1].split('"')[0] + '-' + item.split('"wednesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Thu: ' + item.split('"thursdayOpen":"')[1].split('"')[0] + '-' + item.split('"thursdayClose":"')[1].split('"')[0]
                    hours = hours + '; Fri: ' + item.split('"fridayOpen":"')[1].split('"')[0] + '-' + item.split('"fridayClose":"')[1].split('"')[0]
                    hours = hours + '; Sat: ' + item.split('"saturdayOpen":"')[1].split('"')[0] + '-' + item.split('"saturdayClose":"')[1].split('"')[0]
                    loc = '<MISSING>'
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"pageSize":1000,"range":5000,"latitude":30,"longitude":-105}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = 'murphyusa.com'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if ',"storeNumber":' in item:
                    typ = item.split('"chainName":"')[1].split('"')[0]
                    store = item.split(',"storeNumber":')[1].split(',')[0]
                    name = 'Store #' + store
                    phone = item.split('"phone":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    hours = 'Sun: ' + item.split('"sundayOpen":"')[1].split('"')[0] + '-' + item.split('"sundayClose":"')[1].split('"')[0]
                    hours = hours + '; Mon: ' + item.split('"mondayOpen":"')[1].split('"')[0] + '-' + item.split('"mondayClose":"')[1].split('"')[0]
                    hours = hours + '; Tue: ' + item.split('"tuesdayOpen":"')[1].split('"')[0] + '-' + item.split('"tuesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Wed: ' + item.split('"wednesdayOpen":"')[1].split('"')[0] + '-' + item.split('"wednesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Thu: ' + item.split('"thursdayOpen":"')[1].split('"')[0] + '-' + item.split('"thursdayClose":"')[1].split('"')[0]
                    hours = hours + '; Fri: ' + item.split('"fridayOpen":"')[1].split('"')[0] + '-' + item.split('"fridayClose":"')[1].split('"')[0]
                    hours = hours + '; Sat: ' + item.split('"saturdayOpen":"')[1].split('"')[0] + '-' + item.split('"saturdayClose":"')[1].split('"')[0]
                    loc = '<MISSING>'
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"pageSize":1000,"range":5000,"latitude":30,"longitude":-115}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = 'murphyusa.com'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if ',"storeNumber":' in item:
                    typ = item.split('"chainName":"')[1].split('"')[0]
                    store = item.split(',"storeNumber":')[1].split(',')[0]
                    name = 'Store #' + store
                    phone = item.split('"phone":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    hours = 'Sun: ' + item.split('"sundayOpen":"')[1].split('"')[0] + '-' + item.split('"sundayClose":"')[1].split('"')[0]
                    hours = hours + '; Mon: ' + item.split('"mondayOpen":"')[1].split('"')[0] + '-' + item.split('"mondayClose":"')[1].split('"')[0]
                    hours = hours + '; Tue: ' + item.split('"tuesdayOpen":"')[1].split('"')[0] + '-' + item.split('"tuesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Wed: ' + item.split('"wednesdayOpen":"')[1].split('"')[0] + '-' + item.split('"wednesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Thu: ' + item.split('"thursdayOpen":"')[1].split('"')[0] + '-' + item.split('"thursdayClose":"')[1].split('"')[0]
                    hours = hours + '; Fri: ' + item.split('"fridayOpen":"')[1].split('"')[0] + '-' + item.split('"fridayClose":"')[1].split('"')[0]
                    hours = hours + '; Sat: ' + item.split('"saturdayOpen":"')[1].split('"')[0] + '-' + item.split('"saturdayClose":"')[1].split('"')[0]
                    loc = '<MISSING>'
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"pageSize":1000,"range":5000,"latitude":40,"longitude":-85}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = 'murphyusa.com'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if ',"storeNumber":' in item:
                    typ = item.split('"chainName":"')[1].split('"')[0]
                    store = item.split(',"storeNumber":')[1].split(',')[0]
                    name = 'Store #' + store
                    phone = item.split('"phone":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    hours = 'Sun: ' + item.split('"sundayOpen":"')[1].split('"')[0] + '-' + item.split('"sundayClose":"')[1].split('"')[0]
                    hours = hours + '; Mon: ' + item.split('"mondayOpen":"')[1].split('"')[0] + '-' + item.split('"mondayClose":"')[1].split('"')[0]
                    hours = hours + '; Tue: ' + item.split('"tuesdayOpen":"')[1].split('"')[0] + '-' + item.split('"tuesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Wed: ' + item.split('"wednesdayOpen":"')[1].split('"')[0] + '-' + item.split('"wednesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Thu: ' + item.split('"thursdayOpen":"')[1].split('"')[0] + '-' + item.split('"thursdayClose":"')[1].split('"')[0]
                    hours = hours + '; Fri: ' + item.split('"fridayOpen":"')[1].split('"')[0] + '-' + item.split('"fridayClose":"')[1].split('"')[0]
                    hours = hours + '; Sat: ' + item.split('"saturdayOpen":"')[1].split('"')[0] + '-' + item.split('"saturdayClose":"')[1].split('"')[0]
                    loc = '<MISSING>'
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"pageSize":1000,"range":5000,"latitude":40,"longitude":-95}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = 'murphyusa.com'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if ',"storeNumber":' in item:
                    typ = item.split('"chainName":"')[1].split('"')[0]
                    store = item.split(',"storeNumber":')[1].split(',')[0]
                    name = 'Store #' + store
                    phone = item.split('"phone":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    hours = 'Sun: ' + item.split('"sundayOpen":"')[1].split('"')[0] + '-' + item.split('"sundayClose":"')[1].split('"')[0]
                    hours = hours + '; Mon: ' + item.split('"mondayOpen":"')[1].split('"')[0] + '-' + item.split('"mondayClose":"')[1].split('"')[0]
                    hours = hours + '; Tue: ' + item.split('"tuesdayOpen":"')[1].split('"')[0] + '-' + item.split('"tuesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Wed: ' + item.split('"wednesdayOpen":"')[1].split('"')[0] + '-' + item.split('"wednesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Thu: ' + item.split('"thursdayOpen":"')[1].split('"')[0] + '-' + item.split('"thursdayClose":"')[1].split('"')[0]
                    hours = hours + '; Fri: ' + item.split('"fridayOpen":"')[1].split('"')[0] + '-' + item.split('"fridayClose":"')[1].split('"')[0]
                    hours = hours + '; Sat: ' + item.split('"saturdayOpen":"')[1].split('"')[0] + '-' + item.split('"saturdayClose":"')[1].split('"')[0]
                    loc = '<MISSING>'
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"pageSize":1000,"range":5000,"latitude":40,"longitude":-105}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = 'murphyusa.com'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if ',"storeNumber":' in item:
                    typ = item.split('"chainName":"')[1].split('"')[0]
                    store = item.split(',"storeNumber":')[1].split(',')[0]
                    name = 'Store #' + store
                    phone = item.split('"phone":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    hours = 'Sun: ' + item.split('"sundayOpen":"')[1].split('"')[0] + '-' + item.split('"sundayClose":"')[1].split('"')[0]
                    hours = hours + '; Mon: ' + item.split('"mondayOpen":"')[1].split('"')[0] + '-' + item.split('"mondayClose":"')[1].split('"')[0]
                    hours = hours + '; Tue: ' + item.split('"tuesdayOpen":"')[1].split('"')[0] + '-' + item.split('"tuesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Wed: ' + item.split('"wednesdayOpen":"')[1].split('"')[0] + '-' + item.split('"wednesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Thu: ' + item.split('"thursdayOpen":"')[1].split('"')[0] + '-' + item.split('"thursdayClose":"')[1].split('"')[0]
                    hours = hours + '; Fri: ' + item.split('"fridayOpen":"')[1].split('"')[0] + '-' + item.split('"fridayClose":"')[1].split('"')[0]
                    hours = hours + '; Sat: ' + item.split('"saturdayOpen":"')[1].split('"')[0] + '-' + item.split('"saturdayClose":"')[1].split('"')[0]
                    loc = '<MISSING>'
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"pageSize":1000,"range":5000,"latitude":40,"longitude":-115}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = 'murphyusa.com'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if ',"storeNumber":' in item:
                    typ = item.split('"chainName":"')[1].split('"')[0]
                    store = item.split(',"storeNumber":')[1].split(',')[0]
                    name = 'Store #' + store
                    phone = item.split('"phone":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    hours = 'Sun: ' + item.split('"sundayOpen":"')[1].split('"')[0] + '-' + item.split('"sundayClose":"')[1].split('"')[0]
                    hours = hours + '; Mon: ' + item.split('"mondayOpen":"')[1].split('"')[0] + '-' + item.split('"mondayClose":"')[1].split('"')[0]
                    hours = hours + '; Tue: ' + item.split('"tuesdayOpen":"')[1].split('"')[0] + '-' + item.split('"tuesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Wed: ' + item.split('"wednesdayOpen":"')[1].split('"')[0] + '-' + item.split('"wednesdayClose":"')[1].split('"')[0]
                    hours = hours + '; Thu: ' + item.split('"thursdayOpen":"')[1].split('"')[0] + '-' + item.split('"thursdayClose":"')[1].split('"')[0]
                    hours = hours + '; Fri: ' + item.split('"fridayOpen":"')[1].split('"')[0] + '-' + item.split('"fridayClose":"')[1].split('"')[0]
                    hours = hours + '; Sat: ' + item.split('"saturdayOpen":"')[1].split('"')[0] + '-' + item.split('"saturdayClose":"')[1].split('"')[0]
                    loc = '<MISSING>'
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
