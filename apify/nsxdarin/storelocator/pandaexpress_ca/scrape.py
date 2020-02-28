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
    url = 'https://www.pandaexpress.ca/en/userlocation/searchbycoordinates?lat=34.0667&lng=-118.0833&limit=50&hours=true&_=1582854262229'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        items = line.split('"Id":')
        for item in items:
            if '"Company":"' in item:
                store = item.split(',')[0]
                website = 'pandaexpress.ca'
                loc = '<MISSING>'
                name = item.split('"Name":"')[1].split('"')[0]
                add = item.split('"Address":"')[1].split('"')[0]
                city = item.split('"City":"')[1].split('"')[0]
                state = item.split('"State":"')[1].split('"')[0]
                zc = '<MISSING>'
                phone = item.split('"Phone":"')[1].split('"')[0]
                country = 'CA'
                typ = '<MISSING>'
                lat = item.split('"Latitude":')[1].split(',')[0]
                lng = item.split('"Longitude":')[1].split(',')[0]
                hours = 'Mon: ' + item.split('"Monday":{"StartTime":"')[1].split('"')[0] + '-' + item.split('"Monday":{')[1].split(',"EndTime":"')[1].split('"')[0]
                hours = hours + '; Tue: ' + item.split('"Tuesday":{"StartTime":"')[1].split('"')[0] + '-' + item.split('"Tuesday":{')[1].split(',"EndTime":"')[1].split('"')[0]
                hours = hours + '; Wed: ' + item.split('"Wednesday":{"StartTime":"')[1].split('"')[0] + '-' + item.split('"Wednesday":{')[1].split(',"EndTime":"')[1].split('"')[0]
                hours = hours + '; Thu: ' + item.split('"Thursday":{"StartTime":"')[1].split('"')[0] + '-' + item.split('"Thursday":{')[1].split(',"EndTime":"')[1].split('"')[0]
                hours = hours + '; Fri: ' + item.split('"Friday":{"StartTime":"')[1].split('"')[0] + '-' + item.split('"Friday":{')[1].split(',"EndTime":"')[1].split('"')[0]
                hours = hours + '; Sat: ' + item.split('"Saturday":{"StartTime":"')[1].split('"')[0] + '-' + item.split('"Saturday":{')[1].split(',"EndTime":"')[1].split('"')[0]
                hours = hours + '; Sun: ' + item.split('"Sunday":{"StartTime":"')[1].split('"')[0] + '-' + item.split('"Sunday":{')[1].split(',"EndTime":"')[1].split('"')[0]
                if hours == '':
                    hours = '<MISSING>'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
