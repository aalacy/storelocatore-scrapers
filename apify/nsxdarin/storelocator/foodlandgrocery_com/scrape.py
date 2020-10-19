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
    urls = ['https://foodlandgrocery.com/wp-json/wpgmza/v1/marker-listing/base64eJyrVirIKHDOSSwuVrJSCg9w941yjInxTSzKTi3yySwuycxLj4lxSizOTAbxlHSUiksSi0qUrAwNdJRyUvPSSzIg7NzEgvjMFKARhkq1AK3dG0g','https://foodlandgrocery.com/wp-json/wpgmza/v1/marker-listing/base64eJyrVirIKHDOSSwuVrJSCg9w941yjInxTSzKTi3yySwuycxLj4lxSizOTAbxlHSUiksSi0qUrAx0lHJS89JLMpSsDIHs3MSC+MwUoAmGSrUAlS0bFw']
    for url in urls:
        r = session.get(url, headers=headers)
        website = 'foodlandgrocery.com'
        typ = '<MISSING>'
        country = 'US'
        loc = '<MISSING>'
        store = '<MISSING>'
        hours = '<MISSING>'
        phone = '<MISSING>'
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '{"id":"' in line:
                items = line.split('{"id":"')
                for item in items:
                    if '"map_id":"' in item:
                        name = item.split('"title":"')[1].split('"')[0]
                        addinfo = item.split('"address":"')[1].split('"')[0]
                        lat = item.split('"lat":"')[1].split('"')[0]
                        lng = item.split('"lng":"')[1].split('"')[0]
                        add = addinfo.split(',')[0]
                        city = addinfo.split(',')[1].strip()
                        state = addinfo.split(',')[2].strip().split(' ')[0]
                        zc = addinfo.rsplit(' ',1)[1]
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
