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
    url = 'https://krispykreme.ca/find-a-store/'
    r = session.get(url, headers=headers)
    website = 'krispykreme.ca'
    typ = '<MISSING>'
    country = 'CA'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<div class="location__title h2 text-uppercase">' in line:
            items = line.split('<div class="location__title h2 text-uppercase">')
            for item in items:
                if 'class="location__address">' in item:
                    name = item.split('<')[0].strip()
                    if '<span class="location__subtitle text-light h5"' in name:
                        name = name + ' ' + name.split('<span class="location__subtitle text-light h5"')[1].split('>')[1].split('<')[0].strip()
                    addinfo = item.split('"location__address">')[1].split('iv>')[0].replace('<br /></d','').replace('</d','')
                    if addinfo.count('<br />') == 3:
                        add = addinfo.split('<br />')[0].strip() + ' ' + addinfo.split('<br />')[1].strip()
                        city = addinfo.split('<br />')[2].strip().rsplit(' ',1)[0]
                        state = addinfo.split('<br />')[2].strip().rsplit(' ',1)[1]
                        zc = addinfo.split('<br />')[3].strip()
                    else:
                        add = addinfo.split('<br />')[0].strip()
                        city = addinfo.split('<br />')[1].strip().rsplit(' ',1)[0]
                        state = addinfo.split('<br />')[1].strip().rsplit(' ',1)[1]
                        zc = addinfo.split('<br />')[2].strip()
                    try:
                        phone = item.split('<strong>Tel:</strong>')[1].split('<')[0].strip()
                    except:
                        phone = '<MISSING>'
                    typ = '<MISSING>'
                    store = '<MISSING>'
                    loc = '<MISSING>'
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                    hours = item.split('<div class="location__hours"><div class="font-weight-bold w-100">')[1].split('<br>')[0].replace('</div>','').replace('<div>','').strip()
                    hours = hours.replace('y9','y 9')
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
