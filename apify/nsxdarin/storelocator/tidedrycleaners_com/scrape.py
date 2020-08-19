import csv
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
    weekdays = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
    url = 'https://consumer.tidelaundry.com/v1/servicepoints?maxLatitude=64.93218366344629&maxLongitude=-63.19580074023439&minLatitude=14.87138826455165&minLongitude=-173.33038325976564&statuses=1&statuses=2&statuses=3'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        line = line.replace('"address":{"id":','"address":{"ID')
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if ',"name":"' in item:
                    website = 'tidedrycleaners.com'
                    country = 'US'
                    store = item.split(',')[0]
                    loc = 'https://tidecleaners.com/en-us/locations/' + store
                    name = item.split(',"name":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    add = item.split('streetLine1":"')[1].split('"')[0]
                    try:
                        add = add + ' ' + item.split('streetLine2":"')[1].split('"')[0]
                    except:
                        pass
                    try:
                        city = item.split(',"city":"')[1].split('"')[0]
                    except:
                        city = '<MISSING>'
                    state = item.split('"state":"')[1].split('"')[0]
                    try:
                        zc = item.split('"zipCode":"')[1].split('"')[0]
                    except:
                        zc = '<MISSING>'
                    try:
                        phone = item.split('"phoneNumber":"')[1].split('"')[0]
                    except:
                        phone = '<MISSING>'
                    typ = 'Store'
                    hours = ''
                    days = item.split('hoursOfOperation":[')[1].split(']')[0].split('{"weekday":')
                    for day in days:
                        if '"opensLocal":"' in day:
                            daynum = day.split(',')[0]
                            dayname = weekdays[int(daynum)]
                            hrs = dayname + ': ' + day.split('"opensLocal":"')[1].split('"')[0] + '-' + day.split('"closesLocal":"')[1].split('"')[0]
                            if hours == '':
                                hours = hrs
                            else:
                                hours = hours + '; ' + hrs
                    if hours == '':
                        hours = '<MISSING>'
                    if '"locationTypeId":1' in item:
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
