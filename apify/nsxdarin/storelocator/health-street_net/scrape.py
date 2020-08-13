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
    sms = []
    url = 'https://www.health-street.net/sitemap_index.xml'
    r = session.get(url, headers=headers)
    website = 'health-street.net'
    country = 'US'
    typ = '<MISSING>'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<loc>https://www.health-street.net/location-sitemap' in line:
            sms.append(line.split('<loc>')[1].split('<')[0])
    for sm in sms:
        r2 = session.get(sm, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<loc>https://www.health-street.net/location/' in line2:
                locs.append(line2.split('<loc>')[1].split('<')[0])
    for loc in locs:
        names = []
        print(loc)
        lat = ''
        lng = ''
        hours = ''
        phone = ''
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode('utf-8'))
            if 'Call Now to Register</p><span>' in line2:
                phone = line2.split('Call Now to Register</p><span>')[1].split('<')[0]
            if 'font-weight: bold; font-size: 1.4em;">' in line2:
                items = line2.split('font-weight: bold; font-size: 1.4em;">')
                for item in items:
                    if '<em>Clinic Hours and Information</em>' not in item:
                        hours = ''
                        cname = item.split('</span>')[0].replace('|','-')
                        try:
                            days = item.split('</span><span>')
                            for day in days:
                                if 'day:' in day:
                                    #print(day)
                                    if '<' in day:
                                        hrs = day.split('<')[0]
                                    else:
                                        hrs = day
                                    if hours == '':
                                        hours = hrs
                                    else:
                                        hours = hours + '; ' + hrs
                        except:
                            pass
                        names.append(cname + '|' + hours)
            if ' = new google.maps.Marker(' in line2:
                next(lines)
                next(lines)
                next(lines)
                g = next(lines)
                h = next(lines)
                g = str(g.decode('utf-8'))
                h = str(h.decode('utf-8'))
                lat = g.split(':')[1].split(',')[0]
                lng = h.split(':')[1].split('}')[0].strip().replace('\t','')
            if "openInfoWindow( '<span itemprop=\"streetaddress\">" in line2:
                add = line2.split('"streetaddress">')[1].split('<span')[0].replace('<br>',' ').strip().replace('</span>','')
                city = line2.split('<span itemprop="addresslocality">')[1].split('<')[0]
                state = line2.split('"addressregion">')[1].split('<')[0]
                zc = line2.split('<span itemprop="postalcode">')[1].split('<')[0]
                aname = line2.split('<span itemprop="streetaddress">')[1].split('<')[0]
                for pname in names:
                    if aname == pname.split('|')[0]:
                        hours = pname.split('|')[1]
                ploc = '<MISSING>'
                if hours == '':
                    hours = '<MISSING>'
                store = '<MISSING>'
                hours = hours.replace('&#8211;','-')
                yield [website, ploc, aname, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
