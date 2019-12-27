import csv
import urllib2
import requests
import sgzip

session = requests.Session()
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
    for code in sgzip.for_radius(50):
        print('Pulling Zip Code %s...' % code)
        url = 'https://locations.greyhound.com/bus-stations/search?city=&state=&zip=' + code + '&q='
        r = session.get(url, headers=headers)
        Found = False
        lines = r.iter_lines()
        website = 'greyhound.com'
        typ = '<MISSING>'
        coords = []
        locations = []
        HFound = False
        for line in lines:
            if 'station_hours">' in line:
                HFound = True
            if HFound and '</div>' in line:
                HFound = False
                locinfo = website + '|' + loc + '|' + name + '|' + add + '|' + city + '|' + state + '|' + zc + '|' + country + '|' + store + '|' + phone + '|' + typ + '|' + lat + '|' + lng + '|' + hours
                locations.append(locinfo)
            if HFound and '</B><BR>' in line:
                if hours == '':
                    hours = line.split('<B>')[1].split('<')[0].strip().replace('\t','')
                else:
                    hours = hours + '; ' + line.split('<B>')[1].split('<')[0].strip().replace('\t','')
                g = next(lines)
                hours = hours + ': ' + g.split('<')[0].strip().replace('\t','')
            if 'Tel:' in line:
                phone = line.split('Tel:')[1].split('<')[0].strip()
            if 'station_city_info">' in line:
                phone = '<MISSING>'
                hours = ''
                next(lines)
                g = next(lines)
                h = next(lines)
                if '<B>' in h:
                    loc = 'https://locations.greyhound.com' + g.split('href="')[1].split('"')[0].replace('|','-')
                    store = loc.rsplit('-',1)[1]
                    name = h.split('>')[1].split('<')[0].replace('|','-')
                    next(lines)
                    next(lines)
                    g = next(lines)
                    add = g.split('<')[0].strip().replace('\t','').replace('|','-')
                    h = next(lines)
                    if ', ' not in h:
                        add = add + ' ' + h.split('<')[0].strip().replace('\t','')
                        h = next(lines)
                    csz = h.split('<')[0].strip().replace('\t','').replace('|','-')
                    city = h.split(',')[0].replace('|','-').strip().replace('\t','')
                    zc = h.rsplit(' ',1)[1].replace('|','-').strip().replace('\t','')
                    state = h.split(',')[1].strip().split(' ')[0].strip().replace('\t','')
                    country = 'US'
                    g = next(lines)
                    if 'Bus Stop' in g:
                        typ = 'Bus Stop'
                    else:
                        typ = 'Bus Station'
                else:
                    add = h.split('<')[0].strip().replace('\t','')
                    h = next(lines)
                    csz = h.split('<')[0].strip().replace('\t','').replace('|','-')
                    city = h.split(',')[0].replace('|','-').strip().replace('\t','')
                    zc = h.rsplit(' ',1)[1].replace('|','-').strip().replace('\t','')
                    state = h.split(',')[1].strip().split(' ')[0].strip().replace('\t','')
                    country = 'US'
                lat = '<MISSING>'
                lng = '<MISSING>'
            if 'new L.Marker(new L.LatLng(' in line:
                coords.append(line.split('new L.Marker(new L.LatLng(')[1].split(')')[0].replace(' ',''))
        for x in range(0, len(coords) - 1):
            website = locations[x].split('|')[0]
            loc = locations[x].split('|')[1]
            name = locations[x].split('|')[2]
            add = locations[x].split('|')[3]
            city = locations[x].split('|')[4]
            state = locations[x].split('|')[5]
            zc = locations[x].split('|')[6]
            country = locations[x].split('|')[7]
            store = locations[x].split('|')[8]
            phone = locations[x].split('|')[9]
            typ = locations[x].split('|')[10]
            lat = coords[x].split(',')[0]
            lng = coords[x].split(',')[1]
            hours = locations[x].split('|')[13]
            addinfo = add + city + state
            if addinfo not in ids:
                ids.append(addinfo)
                if '<' in zc:
                    zc = zc.split('<')[0]
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
