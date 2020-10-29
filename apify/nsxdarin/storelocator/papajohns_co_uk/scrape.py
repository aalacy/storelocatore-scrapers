import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('papajohns_co_uk')



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
    addresses = []
    locs.append('https://www.papajohns.co.uk/store-locator.aspx?postcode=G43%202XS')
    locs.append('https://www.papajohns.co.uk/store-locator.aspx?postcode=PA1%203PW')
    locs.append('https://www.papajohns.co.uk/store-locator.aspx?postcode=G11%207BN')
    url = 'https://www.papajohns.co.uk/store-locator.aspx'
    r = session.get(url, headers=headers)
    website = 'papajohns.co.uk'
    typ = '<MISSING>'
    country = 'GB'
    loc = '<MISSING>'
    store = '<MISSING>'
    hours = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '[-3.444468' in line:
            items = line.split('[')
            for item in items:
                if "', '" in item:
                    code = item.split(", '")[6].split("'")[0]
                    lurl = 'https://www.papajohns.co.uk/store-locator.aspx?postcode=' + code.replace(' ','%20')
                    locs.append(lurl)
    lat = '54.594718'
    lng = '-5.801682'
    city = 'Belfast'
    state = 'Co. Antrim'
    hours = '<MISSING>'
    name = 'Belfast'
    add = 'Maxol Spar, 756 Upper Newtownards Road'
    zc = 'BT16 1LA'
    phone = '00 28 9041 9000'
    loc = 'https://papajohns.ie/'
    hours = '<MISSING>'
    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    loc = '<MISSING>'
    store = '<MISSING>'
    hours = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    for loc in locs:
        logger.info(loc)
        Found = True
        hours = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<a id="ctl00_cphBody_hypStoreDetails"' in line2:
                name = line2.split('<a id="ctl00_cphBody_hypStoreDetails"')[1].split('">')[1].split('<')[0]
            if 'var allPoints = new Array ([' in line2:
                lng = line2.split('var allPoints = new Array ([')[1].split(',')[0]
                lat = line2.split('[')[1].split(',')[1].strip()
                add = line2.split('[')[1].split("', '")[1].split("'")[0]
                city = line2.split("', '")[3]
                state = line2.split("', '")[4]
                if state == '':
                    state = '<MISSING>'
                zc = line2.split("', '")[5]
                phone = line2.split("', '")[6].split("'")[0]
            if '<span class="day">' in line2 and Found:
                if hours == '':
                    hours = line2.split('<span class="day">')[1].split('<')[0]
                else:
                    hours = hours + '; ' + line2.split('<span class="day">')[1].split('<')[0]
            if '<div class="storeContacts">' in line2:
                Found = False
            if '<span class="hour">' in line2 and Found:
                hours = hours + ': ' + line2.split('<span class="hour">')[1].split('<')[0]
        if hours == '':
            hours = '<MISSING>'
        info = name + '|' + add
        if info not in addresses:
            addresses.append(info)
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
