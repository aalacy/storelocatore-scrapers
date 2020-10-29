import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tacodelmar_com')



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
    for x in range(0, 125):
        logger.info(('Pulling Location %s...' % str(x)))
        url = 'https://tacodelmar.com/location/?id=' + str(x)
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        website = 'tacodelmar.com'
        lines = r.iter_lines(decode_unicode=True)
        hours = ''
        typ = '<MISSING>'
        store = str(x)
        try:
            for line in lines:
                if '<h3 class="color-turquoise padding-above-below">' in line:
                    name = line.split('<h3 class="color-turquoise padding-above-below">')[1].split('<')[0]
                if 'data-latitude="' in line:
                    lat = line.split('data-latitude="')[1].split('"')[0]
                    lng = line.split('data-longitude="')[1].split('"')[0]
                if '<div class="right-dsc">' in line and '>(' in line:
                    phone = line.split('<div class="right-dsc">')[1].split('<')[0]
                if '<div class="right-dsc">' in line and '>(' not in line:
                    g = next(lines)
                    h = next(lines)
                    add = g.split('<')[0].strip().replace('\t','')
                    csz = h.split('<')[0].strip().replace('\t','')
                    city = csz.split(',')[0]
                    state = csz.split(',')[1].strip().split(' ')[0]
                    zc = csz.split(',')[1].strip().split(' ',1)[1]
                if 'PM<' in line:
                    hrs = line.split('<')[0].strip()
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
            if ' ' in zc:
                country = 'CA'
            else:
                country = 'US'
            if hours == '':
                hours = '<MISSING>'
            if phone == '':
                phone = '<MISSING>'
            canada = ['AB','MB','BC','SK','ON','QC','PQ','NB','NL','NS']
            if state in canada:
                country = 'CA'
            yield [website, url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        except:
            pass

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
