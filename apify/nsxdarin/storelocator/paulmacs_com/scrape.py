import csv
import urllib.request, urllib.error, urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('paulmacs_com')




def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver


session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def fetch_data():
    r = session.get('https://paulmacs.com/', headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    urls = ['https://paulmacs.com/stores-sitemap.xml']
    locs = []
    canada = ['QC', 'AB', 'MB', 'NL', 'PEI',
              'ON', 'NS', 'YT', 'BC', 'NB', 'SK']
    for url in urls:
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '<loc>https://paulmacs.com/location/' in line:
                lurl = line.split('<loc>')[1].split('<')[0]
                locs.append(lurl)
    logger.info(('Found %s Locations.' % str(len(locs))))
    driver = get_driver()
    for loc in locs:
        LocFound = True
        while LocFound:
            LocFound = False
            name = ''
            add = ''
            city = ''
            state = ''
            store = ''
            zc = ''
            phone = ''
            website = 'paulmacs.com'
            typ = 'Store'
            hours = ''
            lat = ''
            country = 'US'
            lng = ''
            # logger.info('Pulling Location %s ...' % loc)

            try:
                driver.get(loc)
                if "down for maintenance" in driver.page_source:
                    logger.info('site is currently down for maintenance')
                    raise SystemExit
                lines = driver.page_source.split('\n')
            except Exception as ex:
                logger.info(('---- trying again after exception: \n %s ---' % ex))
                driver = get_driver()
                driver.get(loc)
                lines = driver.page_source.split('\n')

            for linenum in range(0, len(lines)):
                if 'rel="canonical" href="https://paulmacs.com/location/' in lines[linenum]:
                    store = lines[linenum].split(
                        'rel="canonical" href="https://paulmacs.com/location/')[1].split('/')[0]
                if ',"name":"' in lines[linenum]:
                    typ = lines[linenum].split(',"name":"')[1].split('"')[
                        0]
                    name = lines[linenum].split(',"name":"')[2].split(' |')[
                        0]
                if '<div class="address_info">' in lines[linenum]:
                    g = lines[linenum + 1]
                    if '<br' not in g:
                        g = lines[linenum + 1]
                    if ',' in g.split('<br')[2]:
                        add = g.split('<')[0].strip().replace(
                            '\t', '')
                        city = g.split('<br')[2].split(
                            '>')[1].split(',')[0]
                        state = g.split('<br')[2].split('>')[1].split(
                            ',')[1].strip().split(' ')[0]
                        zc = g.split('<br')[2].split('>')[1].split(',')[1].strip().split(
                            '<')[0].split(' ', 1)[1]
                        if state in canada:
                            country = 'CA'
                            zc = g.split('<br')[2].split('>')[1].split(
                                ',')[1].strip().split(' ', 1)[1]
                    else:
                        if '475 Granville' in g:
                            add = '475 Granville St. North'
                            city = '<MISSING>'
                            state = 'PEI'
                            zc = 'C1N 4P7'
                        else:
                            add = g.split('<')[0].strip().replace(
                                '\t', '')
                            city = g.split('<br')[1].split(
                                '>')[1].split(',')[0]
                            state = g.split('<br')[1].split('>')[1].split(
                                ',')[1].strip().split(' ')[0]
                            zc = g.split('<br')[1].split('>')[1].split(',')[1].strip().split(
                                '<')[0].split(' ', 1)[1]
                        if state in canada:
                            country = 'CA'
                            if add == '475 Granville St. North':
                                zc = 'C1N 4P7'
                            else:
                                zc = g.split('<br')[1].split('>')[1].split(
                                    ',')[1].strip().split(' ', 1)[1]
                    try:
                        phone = g.split('<a href="tel: ')[
                            1].split('"')[0]
                    except:
                        phone = '<MISSING>'
                if 'src="https://www.google.com/maps/' in lines[linenum]:
                    lat = lines[linenum].split('q=')[1].split(',')[
                        0]
                    lng = lines[linenum].split('q=')[1].split(
                        ',')[1].split('&')[0]
                if '<h4>HOURS</h4>' in lines[linenum]:
                    g = lines[linenum + 1]
                    if '<p>' not in g:
                        g = lines[linenum + 1]
                    try:
                        hours = g.split('<p>', 1)[1].split('</div>')[0].replace('</p><p>', '; ').replace('</span><span>', ' ').replace(
                            '<span>', '').replace('</p>', '').replace('</span>', '').strip().replace('\t', '')
                    except:
                        hours = '<MISSING>'
            purl = loc
            if state in canada:
                country = 'CA'
            if add != '':
                if ':' in phone:
                    phone = '<MISSING>'
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            else:
                LocFound = True


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
