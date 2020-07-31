import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.abrazohealth.com//locations/GetFacilities'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '"LocationCode":' in line:
            items = line.split('"LocationCode":')
            for item in items:
                if '{"Uid":"' not in item:
                    lat = item.split('"Latitude":')[1].split(',')[0]
                    add = item.split('"Street":"')[1].split('"')[0]
                    zc = item.split('"Zip":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    lng = item.split('"Longitude":')[1].split(',')[0]
                    website = 'abrazohealth.com'
                    loc = 'https://www.abrazohealth.com/location/detail' + item.split('"DetailUrl":"')[1].split('"')[0]
                    phone = item.split('"Phone":"')[1].split('"')[0]
                    country = 'US'
                    name = item.split('"Title":"')[1].split('"')[0]
                    state = item.split('"StateCode":"')[1].split('"')[0]
                    store = '<MISSING>'
                    hours = ''
                    typ = '<MISSING>'
                    if 'coming-soon' not in loc:
                        print('Pulling Location %s...' % loc)
                        r2 = session.get(loc, headers=headers)
                        Found = False
                        for line2 in r2.iter_lines():
                            line2 = str(line2.decode('utf-8'))
                            if '<div class="w-5/6">' in line2:
                                Found = True
                            if Found and '</div>' in line2:
                                Found = False
                            if Found and '<' in line2 and '<div class' not in line2:
                                hrs = line2.replace('<p>','').split('<')[0]
                                if hours == '':
                                    hours = hrs
                                else:
                                    hours = hours + '; ' + hrs
                        if hours == '':
                            hours = '<MISSING>'
                        if phone == '':
                            phone = '<MISSING>'
                        hours = hours.replace('\t','').strip()
                        if ' Floor' in add:
                            add = add.split(' Floor')[0]
                        if ' Suite' in add:
                            add = add.split(' Suite')[0]
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
