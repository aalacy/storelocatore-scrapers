import csv
import urllib2
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'cookie': '_ga=GA1.2.106458393.1575045458; incap_ses_678_2192629=3OHGJri4GR6CiCOYd9xoCSM1Bl4AAAAAbVS29GeDUW0oCtvQXTLzHQ==; visid_incap_2192629=AswTebp/SjiRWaJU7I5hj1dJ4V0AAAAAQkIPAAAAAACAjSuRAUPcCqa1gZtjwlA1ZikzPTMxfN3/; _gid=GA1.2.246621817.1577465130; _gat_UA-12821136-3=1'
           }

def write_output(data):
    with open('datapaulmacs.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    r = session.get('https://paulmacs.com/', headers=headers)
    urls = ['https://paulmacs.com/stores-sitemap1.xml','https://paulmacs.com/stores-sitemap2.xml']
    locs = []
    canada = ['QC','AB','MB','NL','PEI','ON','NS','YT','BC','NB','SK']
    for url in urls:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<loc>https://paulmacs.com/location/' in line:
                lurl = line.split('<loc>')[1].split('<')[0]
                locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        Found = True
        count = 0
        while Found:
            Found = False
            try:
                count = count + 1
                name = ''
                add = ''
                city = ''
                state = ''
                store = ''
                zc = ''
                phone = ''
                print('Pulling Location %s...' % loc)
                website = 'paulmacs.com'
                typ = 'Store'
                hours = ''
                lat = ''
                country = 'US'
                lng = ''
                r2 = session.get(loc, headers=headers)
                lines = r2.iter_lines()
                for line2 in lines:
                    if 'rel="canonical" href="https://paulmacs.com/location/' in line2:
                        store = line2.split('rel="canonical" href="https://paulmacs.com/location/')[1].split('/')[0]
                    if ',"name":"' in line2:
                        typ = line2.split(',"name":"')[1].split('"')[0]
                        name = line2.split(',"name":"')[3].split(' |')[0]
                    if '<div class="address_info">' in line2:
                        g = next(lines)
                        if '<br' not in g:
                            g = next(lines)
                        add = g.split('<')[0].strip().replace('\t','')
                        city = g.split('<br />')[1].split(',')[0]
                        state = g.rsplit('<br />',1)[1].split(',')[1].strip().split(' ')[0]
                        zc = g.rsplit('<br />',1)[1].split(',')[1].strip().split(' ',1)[1].split('<')[0]
                        try:
                            phone = g.split('<a href="tel: ')[1].split('"')[0]
                        except:
                            phone = '<MISSING>'
                    if 'src="https://www.google.com/maps/' in line2:
                        lat = line2.split('q=')[1].split(',')[0]
                        lng = line2.split('q=')[1].split(',')[1].split('&')[0]
                    if '<h4>HOURS</h4>' in line2:
                        g = next(lines)
                        if '<p>' not in g:
                            g = next(lines)
                        try:
                            hours = g.split('<p>')[1].split('</div>')[0].replace('</p><p>','; ').replace('</span><span>',' ').replace('<span>','').replace('</p>','').replace('</span>','').strip().replace('\t','')
                        except:
                            hours = '<MISSING>'
                purl = loc
                if state in canada:
                    country = 'CA'
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                Found = True
                if count >= 3:
                    Found = False

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
