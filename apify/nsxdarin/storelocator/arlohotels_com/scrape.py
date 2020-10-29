import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('arlohotels_com')



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
    url = 'https://www.arlohotels.com'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<li class="location">' in line:
            items = line.split('<li class="location">')
            for item in items:
                if '<div class="hotel-row"><div id="footer-sidebar2"' not in item and '<a href="/' in item:
                    stub = 'https://www.arlohotels.com/' + item.split('<a href="/')[1].split('"')[0]
                    if 'com//' not in stub:
                        locs.append(stub)
    website = 'arlohotels.com'
    typ = '<MISSING>'
    country = 'US'
    store = '<MISSING>'
    hours = '<MISSING>'
    for loc in locs:
        # logger.info(('Pulling Location %s...' % loc))
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        lat = ''
        lng = ''
        phone = ''
        r2 = session.get(loc, headers=headers)
        base = BeautifulSoup(r2.text,"lxml")
        
        try:
            if "opening" in base.find_all("h1")[1].text.lower():
                continue
        except:
            pass

        name = base.find(id="main-footer").h3.text.strip()
        raw_address = str(base.find(id="main-footer").p.a).replace("<br/","").replace("</a","").split(">")[1:-1]
        add = raw_address[0]
        city = raw_address[-1].split(",")[0].strip()
        state = raw_address[-1].split(",")[1].split()[0].strip()
        zc = raw_address[-1].split(",")[1].split()[1].strip()
        phone = base.find(id="main-footer").p.find_all("a")[-1].text.strip()
        lat = base.find(class_="dwd_map_pin")["data-lat"]
        lng = base.find(class_="dwd_map_pin")["data-lng"]
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
