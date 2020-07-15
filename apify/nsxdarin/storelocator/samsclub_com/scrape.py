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
    url = 'https://www.samsclub.com/sitemap_locators.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<loc>https://www.samsclub.com/club/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    for loc in locs:
        Fuel = False
        print('Pulling Location %s...' % loc)
        website = 'samsclub.com'
        typ = 'Gas'
        hours = ''
        name = ''
        country = 'US'
        city = ''
        add = ''
        zc = ''
        state = ''
        lat = ''
        lng = ''
        phone = ''
        store = loc.rsplit('/',1)[1]
        locurl = 'https://www.samsclub.com/api/node/clubfinder/' + store
        r2 = session.get(locurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '"postalCode":"' in line2:
                Fuel = True
                name = line2.split('"name":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                try:
                    add = line2.split('"address1":"')[1].split('"')[0]
                except:
                    add = ''
                try:
                    add = add + ' ' + line2.split('"address2":"')[1].split('"')[0]
                except:
                    pass
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(',')[0]
                lng = line2.split('"longitude":')[1].split('}')[0]
                fcinfo = line2.split('"operationalHours":{')[1].split(',"geoPoint"')[0]
                days = fcinfo.split('},"')
                for day in days:
                    try:
                        hrs = day.split('"startHr":"')[1].split('"')[0] + '-' + day.split('"endHr":"')[1].split('"')[0]
                        dname = day.split('Hrs":')[0].replace('"','')
                        hrs = dname + ': ' + hrs
                        hrs = hrs.replace('To','-')
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
                    except:
                        pass
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
