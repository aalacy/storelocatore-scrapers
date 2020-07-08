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
    url = 'https://www.earthwisepet.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<loc>https://earthwisepet.com/stores/view/' in line:
            items = line.split('<loc>https://earthwisepet.com/stores/view/')
            for item in items:
                if '</priority></url><url>' in item:
                    lurl = 'https://earthwisepet.com/stores/view/' + item.split('<')[0]
                    if lurl != 'https://earthwisepet.com/stores/view/':
                        locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = '<MISSING>'
        lat = ''
        lng = ''
        hours = ''
        country = 'US'
        zc = ''
        phone = ''
        print('Pulling Location %s...' % loc)
        website = 'earthwisepet.com'
        typ = 'Store'
        acount = 0
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<h3 tabindex="0" class="desc-store">' in line2:
                name = line2.split('<h3 tabindex="0" class="desc-store">')[1].split('<')[0]
            if '<a tabindex="0" href="https://maps.google.com/?q=' in line2:
                acount = acount + 1
                if acount == 2:
                    addinfo = line2.split('<a tabindex="0" href="https://maps.google.com/?q=')[1].split('"')[0].strip()
                    if addinfo.count(',') == 3:
                        add = addinfo.split(',')[0].strip()
                        city = addinfo.split(',')[1].strip()
                        state = addinfo.split(',')[2].strip()
                        zc = addinfo.split(',')[3].strip()
                    else:
                        add = addinfo.split(',')[0].strip() + ' ' + addinfo.split(',')[1].strip()
                        city = addinfo.split(',')[2].strip()
                        state = addinfo.split(',')[3].strip()
                        zc = addinfo.split(',')[4].strip()
            if 'href="tel:' in line2:
                phone = line2.split('href="tel:')[1].split('"')[0].strip()
            if 'google-map" data-lng=' in line2:
                lat = line2.split("data-lat='")[1].split("'")[0]
                lng = line2.split("data-lng='")[1].split("'")[0]
            if 'week-nm">' in line2:
                if hours == '':
                    hours = line2.split('week-nm">')[1].split('<')[0]
                else:
                    hours = hours + '; ' + line2.split('week-nm">')[1].split('<')[0]
            if 'timing">' in line2:
                hours = hours + ': ' + line2.split('timing">')[1].split('<')[0]
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if 'Woodlands' in loc:
            add = '3570 FM 1488, Ste 500'
            city = 'Conroe'
            state = 'TX'
            zc = '77384'
            phone = '936-647-1518'
            lat = '30.228852'
            lng = '-95.5184688'
            hours = '<MISSING>'
        if 'palmharbor' in loc:
            add = '3335 Tampa Rd'
            city = 'Palm Harbor'
            state = 'FL'
            zc = '34684'
            phone = '727-470-9102'
            lat = '28.068362'
            lng = '-82.7235479'
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
