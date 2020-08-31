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
    url = 'https://www.chevrolet.co.uk/dealer-locator-ws-json/servlet/GB/en/meta/?query=Nr+Spalding&queryType=city&format=html&offset=0&limit=26&onlyMatching=false&apps=iconics&orderBy=distance&orderDirection=asc'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"id":' in line:
            line = line.replace('"departments":[{"id":','').replace(']},{"id":','')
            items = line.split('{"id":')
            for item in items:
                if '{"countryCode":"GB"' not in item:
                    locs.append(item.split(',')[0])
    url = 'https://www.chevrolet.co.uk/dealer-locator-ws-json/servlet/GB/en/detail/?'
    for loc in locs:
        url = url + 'ids=' + loc + '&'
    url = url + 'format=html'
    r2 = session.get(url, headers=headers)
    website = 'chevrolet.co.uk'
    typ = '<MISSING>'
    for line2 in r2.iter_lines():
        line2 = str(line2.decode('utf-8'))
        if '{"id":' in line2:
            line2 = line2.replace('"departments":[{"id":','').replace('{"id":1,','')
            items = line2.split('{"id":')
            for item in items:
                if '"code":"' in item:
                    city = item.split('"locality":"')[1].split('"')[0]
                    state = item.split('"region":"')[1].split('"')[0]
                    store = item.split(',')[0]
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    add = item.split('"street":"')[1].split('"')[0]
                    phone = item.split('"html":"tel: ')[1].split('"')[0]
                    loc = '<MISSING>'
                    name = item.split(',"formatted":{"html":"')[1].split('"')[0].strip()
                    country = 'GB'
                    lng = item.split('"longitude":')[1].split(',')[0]
                    lat = item.split(',"latitude":')[1].split('}')[0]
                    hours = '<MISSING>'
                    if 'Parts USA' in name:
                        city = 'Stockport'
                    state = state.replace('England, ','')
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
