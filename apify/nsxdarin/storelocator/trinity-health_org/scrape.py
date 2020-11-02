import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('trinity-health_org')



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
    locinfo = []
    locs = []
    for x in range(0, 20):
        logger.info(x)
        loc = 'https://www.trinity-health.org/find-a-location/location-results?page=' + str(x) + '&count='
        r = session.get(loc, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '"DirectUrl\\":\\"' in line:
                items = line.split('"DirectUrl\\":\\"')
                for item in items:
                    if '"LocationName\\":\\"\\"' in item:
                        lurl = 'https://www.trinity-health.org/' + item.split('\\')[0]
                        locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ''
        website = 'trinity-health.org'
        typ = '<MISSING>'
        add = ''
        state = ''
        city = ''
        zc = ''
        country = 'US'
        store = '<MISSING>'
        phone = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '"Name\\\\\\":\\\\\\"' in line2:
                name = line2.split('"Name\\\\\\":\\\\\\"')[1].split('\\')[0]
            if '"Address1\\\\\\":\\\\\\"' in line2:
                add = line2.split('"Address1\\\\\\":\\\\\\"')[1].split('\\')[0]
            if '"Address2\\\\\\":\\\\\\"' in line2:
                add = add + ' ' + line2.split('"Address2\\\\\\":\\\\\\"')[1].split('\\')[0]
                add = add.strip()
            if '"City\\\\\\":\\\\\\"' in line2:
                city = line2.split('"City\\\\\\":\\\\\\"')[1].split('\\')[0]
            if '"PostalCode\\\\\\":\\\\\\"' in line2:
                zc = line2.split('"PostalCode\\\\\\":\\\\\\"')[1].split('\\')[0]
            if '"Phone\\\\\\":\\\\\\"' in line2:
                phone = line2.split('"Phone\\\\\\":\\\\\\"')[1].split('\\')[0]
            if '"StateName\\\\\\":\\\\\\"' in line2:
                state = line2.split('"StateName\\\\\\":\\\\\\"')[1].split('\\')[0]
            if 'Latitude\\\\\\":' in line2:
                lat = line2.split('Latitude\\\\\\":')[1].split(',')[0]
            if 'Longitude\\\\\\":' in line2:
                lng = line2.split('Longitude\\\\\\":')[1].split(',')[0]
            if '"Values\\":[\\"' in line2:
                hours = line2.split('"Values\\":[\\"')[1].split('\\"],\\"')[0].replace('",\\"','; ').replace('"','')
        if phone == '':
            phone = '<MISSING>'
        info = add + ':' + city
        if hours == '':
            hours = '<MISSING>'
        if info not in locinfo:
            locinfo.append(info)
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
