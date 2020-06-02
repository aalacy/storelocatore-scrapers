import csv
import urllib2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sgrequests import SgRequests
chrome_options = Options()

chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
        LocFound = True
        while LocFound:
            LocFound = False
            driver.get(loc)
            Found = True
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
            lines = driver.page_source.split('\n')
            for linenum in range(0, len(lines)):
                if 'rel="canonical" href="https://paulmacs.com/location/' in lines[linenum]:
                    store = lines[linenum].split('rel="canonical" href="https://paulmacs.com/location/')[1].split('/')[0].encode('utf-8')
                if ',"name":"' in lines[linenum]:
                    typ = lines[linenum].split(',"name":"')[1].split('"')[0].encode('utf-8')
                    name = lines[linenum].split(',"name":"')[2].split(' |')[0].encode('utf-8')
                if '<div class="address_info">' in lines[linenum]:
                    g = lines[linenum + 1]
                    if '<br' not in g:
                        g = lines[linenum + 1]
                    if ',' in g.split('<br')[2]:
                        add = g.split('<')[0].strip().replace('\t','').encode('utf-8')
                        city = g.split('<br')[2].split('>')[1].split(',')[0].encode('utf-8')
                        state = g.split('<br')[2].split('>')[1].split(',')[1].strip().split(' ')[0].encode('utf-8')
                        zc = g.split('<br')[2].split('>')[1].split(',')[1].strip().split('<')[0].split(' ',1)[1].encode('utf-8')
                        if state in canada:
                            country = 'CA'
                            zc = g.split('<br')[2].split('>')[1].split(',')[1].strip().split(' ',1)[1]
                    else:
                        if '475 Granville' in g:
                            add = '475 Granville St. North'
                            city = '<MISSING>'
                            state = 'PEI'
                            zc = 'C1N 4P7'
                        else:
                            add = g.split('<')[0].strip().replace('\t','').encode('utf-8')
                            city = g.split('<br')[1].split('>')[1].split(',')[0].encode('utf-8')
                            state = g.split('<br')[1].split('>')[1].split(',')[1].strip().split(' ')[0].encode('utf-8')
                            zc = g.split('<br')[1].split('>')[1].split(',')[1].strip().split('<')[0].split(' ',1)[1].encode('utf-8')
                        if state in canada:
                            country = 'CA'
                            if add == '475 Granville St. North':
                                zc = 'C1N 4P7'
                            else:
                                zc = g.split('<br')[1].split('>')[1].split(',')[1].strip().split(' ',1)[1]
                    try:
                        phone = g.split('<a href="tel: ')[1].split('"')[0].encode('utf-8')
                    except:
                        phone = '<MISSING>'
                if 'src="https://www.google.com/maps/' in lines[linenum]:
                    lat = lines[linenum].split('q=')[1].split(',')[0].encode('utf-8')
                    lng = lines[linenum].split('q=')[1].split(',')[1].split('&')[0].encode('utf-8')
                if '<h4>HOURS</h4>' in lines[linenum]:
                    g = lines[linenum + 1]
                    if '<p>' not in g:
                        g = lines[linenum + 1]
                    try:
                        hours = g.split('<p>',1)[1].split('</div>')[0].replace('</p><p>','; ').replace('</span><span>',' ').replace('<span>','').replace('</p>','').replace('</span>','').strip().replace('\t','').encode('utf-8')
                    except:
                        hours = '<MISSING>'
            purl = loc
            if state in canada:
                country = 'CA'
            if add != '':
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            else:
                LocFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
