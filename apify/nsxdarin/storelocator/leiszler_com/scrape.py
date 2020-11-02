import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import os

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
    coords = []
    places = []
    url = 'https://www.leiszler.com/locations/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if 'var infowindow = new google.maps' in line:
            title = line.split('"title">')[1].split('<')[0].replace('&#039;',"'")
            g = next(lines)
            latlng = g.split('new google.maps.LatLng(')[1].split(',')[0] + '|' + g.split(', ')[1].split(')')[0]
            coords.append(title + '|' + latlng)
        if 'class="img-responsive" /><a href="https://www.leiszler.com/locations/location/' in line:
            items = line.split('class="img-responsive" /><a href="')
            for item in items:
                if '<div class="row location-rows">' not in item:
                    loc = item.split('"')[0]
                    name = item.split('<span itemprop="name">')[1].split('<')[0]
                    try:
                        phone = item.split('itemprop="telephone">')[1].split('<')[0]
                    except:
                        phone = '<MISSING>'
                    hours = '<MISSING>'
                    website = 'leiszler.com'
                    add = item.split('"streetAddress">')[1].split('<')[0]
                    city = item.split('"addressLocality">')[1].split('<')[0]
                    zc = item.split('"postalCode">')[1].split('<')[0]
                    state = item.split('"addressRegion">')[1].split('<')[0]
                    country = 'US'
                    store = '<MISSING>'
                    typ = 'Store'
                    hours = '<MISSING>'
                    info = website + '|' + loc + '|' + name + '|' + add + '|' + city + '|' + state + '|' + zc + '|' + country + '|' + store + '|' + phone + '|' + typ + '|' + hours
                    places.append(info)
    for item in coords:
        for place in places:
            if place.split('|')[2] == item.split('|')[0]:
                lat = item.split('|')[1]
                lng = item.split('|')[2]
                website = place.split('|')[0]
                loc = place.split('|')[1]
                name = place.split('|')[2]
                add = place.split('|')[3]
                city = place.split('|')[4]
                state = place.split('|')[5]
                zc = place.split('|')[6]
                country = place.split('|')[7]
                store = place.split('|')[8]
                phone = place.split('|')[9]
                typ = place.split('|')[10]
                hours = place.split('|')[11]
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
