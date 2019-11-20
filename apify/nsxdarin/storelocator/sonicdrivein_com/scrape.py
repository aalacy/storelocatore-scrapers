import csv
import urllib2
import requests

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
    url = 'https://locations.sonicdrivein.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<xhtml:link rel="alternate" hreflang="en" href="' in line:
            lurl = line.split('<xhtml:link rel="alternate" hreflang="en" href="')[1].split('"')[0]
            if lurl.count('/') == 5 and lurl not in locs:
                locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        print('Pulling Location %s...' % loc)
        url = loc
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        phone = ''
        hours = ''
        lat = ''
        lng = ''
        store = ''
        name = 'Sonic Drive-In'
        website = 'sonicdrivein.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '</head><body>' in line2:
                store = line2.split(',"id":')[1].split(',')[0]
                lat = line2.split(',"latitude":')[1].split(',')[0]
                lng = line2.split(',"longitude":')[1].split(',')[0]
                try:
                    phone = line2.split('itemprop="telephone" id="telephone">')[1].split('<')[0].strip()
                except:
                    pass
                addinfo = line2.split('itemtype="http://schema.org/PostalAddress"')[1].split('</address>')[0]
                add = addinfo.split('<span class="c-address-street-1">')[1].split('<')[0].strip()
                try:
                    add = add + ' ' + addinfo.split('<span class="c-address-street-2">')[1].split('<')[0].strip()
                except:
                    pass
                city = addinfo.split('itemprop="addressLocality">')[1].split('<')[0].strip()
                state = addinfo.split('itemprop="addressRegion">')[1].split('<')[0].strip()
                country = addinfo.split('itemprop="addressCountry">')[1].split('<')[0].strip()
                zc = addinfo.split('itemprop="postalCode">')[1].split('<')[0].strip()
                dayinfo = line2.split("data-days='[")[1].split(']}]')[0]
                days = dayinfo.split('"day":"')
                for day in days:
                    if '"intervals":' in day:
                        if '"end":' not in day:
                            if hours == '':
                                hours = day.split('"')[0] + ': Closed'
                            else:
                                hours = hours + '; ' + day.split('"')[0] + ': Closed'
                        else:
                            if hours == '':
                                endtime = day.split('"end":')[1].split(',')[0]
                                if endtime == '0':
                                    endtime = '0000'
                                hours = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + endtime
                            else:
                                hours = hours + '; ' + day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + endtime
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
