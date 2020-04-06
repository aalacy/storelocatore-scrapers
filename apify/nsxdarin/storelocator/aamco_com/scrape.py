import csv
import urllib2
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
    canada = ['ON','SK','AB','NB','NL','PQ','QC','NS','BC','PEI','PE','NU','YK']
    url = 'https://www.aamco.com/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.aamco.com/Auto-Repair-Center/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'aamco.com'
        name = ''
        store = '<MISSING>'
        lat = ''
        lng = ''
        hours = ''
        phone = ''
        add = ''
        city = ''
        zc = ''
        typ = '<MISSING>'
        state = loc.split('https://www.aamco.com/Auto-Repair-Center/')[1].split('/')[0]
        if state in canada:
            country = 'CA'
        else:
            country = 'US'
        hours = ''
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        HFound = False
        for line2 in lines:
            if '<div class="row storehours">' in line2:
                HFound = True
            if HFound and '</div>' in line2:
                HFound = False
            if HFound and '<p><span>' in line2:
                hrs = line2.split('<p><span>')[1].split('</p')[0].replace('</span>',':')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '<h2 class="title02">' in line2 and name == '':
                name = line2.split('<h2 class="title02">')[1].split('<')[0].strip()
            if '<span class="smalltxt">Address</span>' in line2:
                g = next(lines)
                if 'IL/Waukegan/S-Green-Bay-Rd' in loc:
                    add = '69 South Green Bay Road'
                    city = 'Waukegan'
                    zc = '60085'
                elif 'Medford-Ave,' in loc:
                    add = '638 Medford Ave. Rt 112'
                    city = 'Patchogue'
                    state = 'NY'
                    zc = '11772'
                else:
                    addinfo = g.split('<')[0].strip().replace('\t','').replace(', Canada','').strip()
                    add = addinfo.split(',')[0]
                    city = addinfo.split(',')[1].strip()
                    if country == 'US':
                        zc = addinfo.rsplit(' ',1)[1]
                    else:
                        zc = addinfo.rsplit(' ',2)[1] + ' ' + addinfo.rsplit(' ',1)[1]
            if 'Phone</span>' in line2:
                try:
                    phone = next(lines).split('">')[1].split('<')[0]
                except:
                    phone = '<MISSING>'
            if 'var uluru = { lat:' in line2:
                lat = line2.split('var uluru = { lat:')[1].split(',')[0].strip()
                lng = line2.split('lng:')[1].split('}')[0].strip()
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if city == '#102':
            city = 'El Paso'
            add = '1407 Lomaland Dr. #102'
        if city == '#13':
            city = 'Santa Clarita'
            add = '25845 Railroad Avenue #13'
        if city == '#A':
            city = 'Willoughby'
            add = '36705 Euclid Ave. #A'
        if city == 'Harbor City':
            zc = '90710'
        if 'Eglinton' in add or 'Manitou' in add or 'Hopkins St' in add:
            state = 'ON'
            zc = '<MISSING>'
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
