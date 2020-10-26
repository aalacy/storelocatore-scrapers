import csv
import us
import re
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('coffeebean_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

ignore_url_strings = ['bahrain', 'bangladesh', 'brunei', 'cambodia', 'egypt', 'germany', 'india', 'indonesia', 'israel',
                      'japan', 'korea', 'kurdistan', 'kuwait', 'malaysia', 'mongolia', 'oman', 'pakistan', 'panama',
                      'paraguay', 'philippines', 'qatar', 'saudi-arabia', 'singapore', 'sri-lanka', 'thailand', 'vietnam']

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    for x in range(0, 101):
        # logger.info('Pulling Page %s... ' % str(x))
        url = 'https://www.coffeebean.com/store-locator?field_geo_location_boundary%5Blat_north_east%5D=&field_geo_location_boundary%5Blng_north_east%5D=&field_geo_location_boundary%5Blat_south_west%5D=&field_geo_location_boundary%5Blng_south_west%5D=&field_country_value=&field_street_address_value=&field_city_value=&field_postal_code_value=&page=' + str(x)
        r = session.get(url, headers=headers)
        for line in r.iter_lines(decode_unicode=True):
            if 'View Store</a>' in line:
                # logger.info(line)
                lurl = line.split('href="')[1].split('"')[0]
                if any(x in lurl for x in ignore_url_strings): 
                    continue
                if ('/store/' in lurl or '/node/' in lurl) and lurl not in locs:
                    locs.append(lurl)
    # logger.info('Found %s Locations...' % str(len(locs)))
    for loc in locs:
        r = session.get(loc, headers=headers)
        # logger.info('Pulling Location %s ... ' % loc)
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        typ = '<MISSING>'
        country = ''
        store = '<MISSING>'
        phone = '<MISSING>'
        lat = ''
        lng = ''
        hours = ''
        website = 'coffeebean.com'
        for line in r.iter_lines(decode_unicode=True):
            if '<span class="field-content">' in line:
                name = line.split('<span class="field-content">')[1].split('<')[0]
            if '<span property="streetAddress">' in line:
                add = line.split('<span property="streetAddress">')[1].split('<')[0]
            if '<span property="addressLocality">' in line:
                city = line.split('<span property="addressLocality">')[1].split('<')[0]
            if '<span property="addressRegion">' in line:
                state = line.split('<span property="addressRegion">')[1].split('<')[0]
            if '<span property="addressCountry">' in line:
                country = line.split('<span property="addressCountry">')[1].split('<')[0]
                # remove non-alpha characters
                country = re.sub(r'[^a-zA-Z\s]', '', country)
                if country == 'United States': 
                    country = 'USA'
            if '<span property="telephone">' in line: 
                phone = line.split('<span property="telephone">')[1].split('<')[0]
            if '<span property="postalCode">' in line:
                zc = line.split('<span property="postalCode">')[1].split('<')[0]
            if '<meta property="latitude" content="' in line:
                lat = line.split('<meta property="latitude" content="')[1].split('"')[0]
            if '<meta property="longitude" content="' in line:
                lng = line.split('<meta property="longitude" content="')[1].split('"')[0]
            if 'name-field-weekday' in line:
                day = line.split('">')[1].split('<')[0]
            if 'name-field-store-open' in line:
                hro = line.split('">')[1].split('<')[0]
            if 'name-field-store-closed' in line:
                hrs = day + ': ' + hro + '-' + line.split('">')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if lat == '':
            lat = '<MISSING>'
            lng = '<MISSING>'
        if name == '':
            name = city
        if add == '':
            add = '<MISSING>'
        if zc == '':
            zc = '<MISSING>'
        if country in ['', 'NULL']: 
          # logger.info('country is empty or null ... looking up state: ', state)
          if us.states.lookup(state): 
              country = 'USA'
              # logger.info('state is USA')
        if country != 'USA': 
            # logger.info('skipping country ', country)
            continue
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
