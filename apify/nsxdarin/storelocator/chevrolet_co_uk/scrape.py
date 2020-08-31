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
    website = 'chevrolet.co.uk'
    cities = ['London','Belfast','Aberdeen']
    for city in cities:
        url = 'https://www.chevrolet.co.uk/OCRestServices/dealer/city/v1/faw/' + city + '?distance=500&maxResults=50'
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '{"dealerName":"' in line:
                items = line.split('{"dealerName":"')
                for item in items:
                    if 'legalEntityName' in item:
                        name = item.split('"')[0]
                        loc = item.split(',"dealerUrl":"')[1].split('"')[0]
                        phone = item.split('"phone1":"')[1].split('"')[0]
                        city = item.split('"cityName":"')[1].split('"')[0]
                        add = item.split('"addressLine1":"')[1].split('"')[0]
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        country = item.split('"countryCode":"')[1].split('"')[0]
                        state = '<MISSING>'
                        lat = item.split('"latitude":')[1].split(',')[0]
                        lng = item.split('"longitude":')[1].split('}')[0]
                        if 'Stockport' in city:
                            city = 'Stockport'
                            add = add + ' Bredbury Park Way'
                        store = '<MISSING>'
                        typ = '<MISSING>'
                        hours = '<MISSING>'
                        if name not in locs:
                            locs.append(name)
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
