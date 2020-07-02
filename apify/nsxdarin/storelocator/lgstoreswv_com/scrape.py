import csv
from sgselenium import SgSelenium

driver = SgSelenium().chrome() 

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://lgstoreswv.com/locations/'
    driver.get(url)
    state = 'WV'
    website = 'lgstoreswv.com'
    country = 'US'
    hours = '<MISSING>'
    lines = driver.page_source.split('\n')
    for linenum in range(0, len(lines)):
        if '"marker_id":"' in lines[linenum]:
            items = lines[linenum].split('"marker_id":"')
            for item in items:
                if '"address":"' in item:
                    if '"title":"' in item:
                        name = item.split('"title":"')[1].split('"')[0]
                        store = item.split('STORE#')[1].split('\\')[0]
                    if '<\\/strong><\\/p><p>' in item:
                        addinfo = item.split('<\\/strong><\\/p><p>')[1].split('<\\/span><\\/')[0]
                    if '><p class=\\"p1\\"><span class=\\"s1\\">' in item:
                        addinfo = item.split('><p class=\\"p1\\"><span class=\\"s1\\">')[1].split('<\\/span><\\/')[0]
                    if '/p><p><strong>' in addinfo:
                        addinfo = addinfo.split('/p><p><strong>')[0]
                    addinfo = addinfo.replace('\\/span><span class=\\"s1\\">','')
                    add = addinfo.split(',')[0]
                    city = addinfo.split(',')[1].strip()
                    zc = addinfo.rsplit(' ',1)[1]
                    if '>304-' in item:
                        phone = '304-' + item.split('>304-')[1].split(' ')[0]
                        phone = phone.split('<')[0]
                    else:
                        phone = '<MISSING>'
                    typ = name
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    purl = '<MISSING>'
                    if '<' in store:
                        store = store.split('<')[0]
                    if '<' in zc:
                        zc = zc.split('<')[0]
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
