import csv
from sgrequests import SgRequests
import json
from sgzip import sgzip

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
    ids = []
    for coord in sgzip.coords_for_radius(50):
        x = coord[0]
        y = coord[1]
        url = 'https://www.curves.com/find-a-club?location=10002&lat=' + str(x) + '&lng=' + str(y)
        r = session.get(url, headers=headers)
        for raw_line in r.iter_lines():
            line = str(raw_line)
            if '>&#x1F4DE;</i>' in line:
                phone = line.split('>&#x1F4DE;</i>')[1].split('<')[0]
            if '<a href="https://www.wellnessliving.com' in line:
                purl = line.split('href="')[1].split('"')[0]
                if purl not in ids:
                    ids.append(purl)
                    r2 = session.get(purl, headers=headers)
                    name = ''
                    website = 'curves.com'
                    typ = 'Fitness Studio'
                    add = ''
                    city = ''
                    state = ''
                    zc = ''
                    country = 'US'
                    store = '<MISSING>'
                    lat = ''
                    lng = ''
                    hours = ''
                    for raw_line2 in r2.iter_lines():
                        line2 = str(raw_line2)
                        if '<meta name="geo.position" content="' in line2:
                            lat = line2.split('<meta name="geo.position" content="')[1].split(';')[0]
                            lng = line2.split('<meta name="geo.position" content="')[1].split(';')[1].split('"')[0]
                        if '"geo.placename" content="' in line2:
                            name = line2.split('"geo.placename" content="')[1].split('"')[0]
                        if 'margin:0;">  <li> <img alt="' in line2:
                            typ = line2.split('margin:0;">  <li> <img alt="')[1].split(' in ')[0]
                        if '<span itemprop="streetAddress">' in line2:
                            add = line2.split('<span itemprop="streetAddress">')[1].split('<')[0]
                            city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
                            state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
                            zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
                        if 'class="rs-microsite-right-day-column"><span>' in line2:
                            alldays = []
                            allhrs = []
                            days = line2.split('right-day-column">')[1].split('<br /></div>')[0].split('<br />')
                            for day in days:
                                if '</span>' in day:
                                    dname = day.rsplit('>')[1].split('<')[0]
                                    alldays.append(dname)
                            hrs = line2.split('right-time-column">')[1].split('<br /></div>')[0].split('<br />')
                            for hour in hrs:
                                if '</span>' in hour:
                                    if hour.count('</span>') == 1:
                                        allhrs.append(hour.split('>')[1].split('<')[0])
                                    else:
                                        allhrs.append(hour.split('</span>')[1])
                            for x in range(0, len(alldays)):
                                if hours == '':
                                    hours = alldays[x] + ': ' + allhrs[x]
                                else:
                                    hours = hours + '; ' + alldays[x] + ': ' + allhrs[x]
                    if hours == '':
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    if add != '':
                        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
