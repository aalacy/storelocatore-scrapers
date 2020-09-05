import csv
import urllib.request, urllib.error, urllib.parse
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
    url = 'https://apps.hac.ca/api/getdealers?numberdealers=1000&languagecode=en&latitude=49.2827291&longitude=-123.1207375'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    info = ''
    for line in r.iter_lines(decode_unicode=True):
        info = info + line.replace('\r','').replace('\t','').replace('\n','').strip()
    items = info.split('{"SortOrder":"')
    for item in items:
        if '"DealerCode":"' in item:
            website = 'hyundaicanada.com'
            typ = '<MISSING>'
            hours = ''
            store = item.split('"DealerCode":"')[1].split('"')[0]
            phone = item.split('"Phone":"')[1].split('"')[0]
            city = item.split('"City":"')[1].split('"')[0]
            add = item.split('"Street":"')[1].split('"')[0]
            zc = item.split('"PostalCode":"')[1].split('"')[0]
            country = 'CA'
            name = item.split('"Name":"')[1].split('"')[0]
            lat = item.split('"Latitude":"')[1].split('"')[0]
            lng = item.split('"Longitude":"')[1].split('"')[0]
            state = item.split('"ProvinceShortName":"')[1].split('"')[0]
            days = item.split('"Sales":{"Days":[{')[1].split(']},')[0].split('"Weekday":"')
            for day in days:
                if '"Start":"' in day:
                    hrs = day.split('"')[0] + ': ' + day.split('"Start":"')[1].split('"')[0] + '-' + day.split('"End":"')[1].split('"')[0]
                    hrs = hrs.replace('Closed-Closed','Closed')
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
            loc = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
