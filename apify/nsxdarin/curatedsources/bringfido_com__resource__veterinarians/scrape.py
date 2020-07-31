import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'accept': 'application/json'
           }
headers1 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    numbers = ['0','1','2','3','4','5','6','7','8','9']
    page = -24
    Found = True
    while Found:
        page = page + 24
        Found = False
        print(page)
        url = 'https://www.bringfido.com/resource/?region=united_states&type=V&start=' + str(page) + '&__amp_source_origin=https%3A%2F%2Fwww.bringfido.com'
        r = session.get(url, headers=headers)
        website = 'bringfido.com'
        country = 'US'
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '{"website": "' in line:
                items = line.split('{"website": "')
                for item in items:
                    if '"thumbnail@3x":' in item:
                        Found = True
                        loc = 'https://bringfido.com' + item.split('"url": "')[1].split('"')[0]
                        store = item.split('"id": ')[1].split('}')[0]
                        typ = '<MISSING>'
                        add = item.split('"address": "')[1].split('"')[0]
                        lat = item.split('"latitude": ')[1].split(',')[0]
                        lng = item.split('"longitude": ')[1].split(',')[0]
                        csc = item.split('"full_name": "')[1].split('"')[0]
                        city = csc.split(',')[0]
                        state = csc.split(',')[1].strip()
                        if ',' in add:
                            add = add.split(',')[0].strip()
                        zc = '<MISSING>'
                        name = item.split('"name": "')[1].split('"')[0].replace('\\u2013','-')
                        hours = '<MISSING>'
                        phone = '<MISSING>'
                        r2 = session.get(loc, headers=headers1)
                        for line2 in r2.iter_lines():
                            line2 = str(line2.decode('utf-8'))
                            if '"address": "' in line2:
                                zc = line2.split('"address": "')[1].split('"')[0].rsplit(' ',1)[1].strip()
                                if zc[-1] not in numbers and zc[0] not in numbers:
                                    zc = '<MISSING>'
                            if '<a href="tel:+' in line2:
                                phone = line2.split('<a href="tel:+')[1].split('"')[0]
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

    page = -24
    Found = True
    while Found:
        page = page + 24
        Found = False
        print(page)
        url = 'https://www.bringfido.com/resource/?region=canada&type=V&start=' + str(page) + '&__amp_source_origin=https%3A%2F%2Fwww.bringfido.com'
        r = session.get(url, headers=headers)
        website = 'bringfido.com'
        country = 'CA'
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '{"website": "' in line:
                items = line.split('{"website": "')
                for item in items:
                    if '"thumbnail@3x":' in item:
                        Found = True
                        loc = 'https://bringfido.com' + item.split('"url": "')[1].split('"')[0]
                        store = item.split('"id": ')[1].split('}')[0]
                        typ = '<MISSING>'
                        add = item.split('"address": "')[1].split('"')[0]
                        lat = item.split('"latitude": ')[1].split(',')[0]
                        lng = item.split('"longitude": ')[1].split(',')[0]
                        csc = item.split('"full_name": "')[1].split('"')[0]
                        city = csc.split(',')[0]
                        state = csc.split(',')[1].strip()
                        if ',' in add:
                            add = add.split(',')[0].strip()
                        zc = '<MISSING>'
                        name = item.split('"name": "')[1].split('"')[0].replace('\\u2013','-')
                        hours = '<MISSING>'
                        phone = '<MISSING>'
                        r2 = session.get(loc, headers=headers1)
                        for line2 in r2.iter_lines():
                            line2 = str(line2.decode('utf-8'))
                            if '"address": "' in line2:
                                zc = line2.split('"address": "')[1].split('"')[0].rsplit(' ',1)[1].strip()
                                if zc[-1] not in numbers and zc[0] not in numbers:
                                    zc = '<MISSING>'
                            if '<a href="tel:+' in line2:
                                phone = line2.split('<a href="tel:+')[1].split('"')[0]
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
