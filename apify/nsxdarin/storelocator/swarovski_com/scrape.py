import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

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
    ids = []
    coords = ['21,-155','60,-150','47,-122','33,-95','53,-95','35,-75','55,-75']
    for item in coords:
        lat = item.split(',')[0]
        lng = item.split(',')[1]
        print(('%s - %s...' % (lat, lng)))
        rad = 1000
        if lng == '-95':
            rad = 500
        url = 'https://www.swarovski.com/en-US/store-finder/list/?allBaseStores=true&geoPoint.latitude=' + str(lat) + '&geoPoint.longitude=' + str(lng) + '&radius=' + str(rad)
        website = 'swarovski.com'
        typ = ''
        hours = ''
        r = session.get(url, headers=headers)
        if '{"results":[{"name":' in r.content:
            items = r.content.split('{"name":"')
            for item in items:
                if ',"displayName":"' in item:
                    store = item.split('"')[0]
                    hours = ''
                    name = item.split('"displayName":"')[1].split('"')[0]
                    typ = item.split('"distributionType":"')[1].split('"')[0]
                    loc = 'https://www.swarovski.com/en-US' + item.split('"url":"')[1].split('"')[0]
                    if '?' in loc:
                        loc = loc.split('?')[0]
                    lat = item.split('"geoPoint":{"latitude":')[1].split(',')[0]
                    lng = item.split('"geoPoint":{"latitude":')[1].split(',"longitude":')[1].split('}')[0]
                    add = item.split('"line1":"')[1].split('"')[0]
                    try:
                        city = item.split('"town":"')[1].split('"')[0]
                    except:
                        city = '<MISSING>'
                    country = item.split('"country":{"isocode":"')[1].split('"')[0]
                    try:
                        state = item.split('"isocodeShort":"')[1].split('"')[0]
                    except:
                        state = '<MISSING>'
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    days = item.split('"weekDayOpeningList":[{')[1].split('}],"specialDayOpeningList":')[0].split('},{')
                    for day in days:
                        if '"closed":true' in day:
                            hrs = day.split('"weekDay":"')[1].split('"')[0] + ': Closed'
                        else:
                            try:
                                hrs = day.split('"weekDay":"')[1].split('"')[0] + ': ' + day.split('"openingTime":')[1].split('"formattedHour":"')[1].split('"')[0] + '-' + day.split('"closingTime":')[1].split('"formattedHour":"')[1].split('"')[0]
                            except:
                                hours = '<MISSING>'
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
                    if hours == '' or '00' not in hours or '<MISSING>' in hours:
                        hours = '<MISSING>'
                    if store not in ids:
                        if 'HALLMARK STERLING RIDGE' in name:
                            name = "TRUDY'S HALLMARK STERLING RIDGE"
                        if country == 'CA' or country == 'US':
                            ids.append(store)
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
