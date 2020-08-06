import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

driver = webdriver.Chrome("chromedriver")

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.costco.com/sitemap_l_001.xml'
    driver.get(url)
    lines = driver.page_source.split('\n')
    for linenum in range(0, len(lines)):
        g = g
        g = str(g.decode('utf-8'))
        if '<loc>https://www.costco.com/warehouse-locations/' in g:
            locs.append(g.split('<loc>')[1].split('<')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'costco.com/gasoline.html'
        typ = 'Gas'
        hours = ''
        phone = ''
        add = ''
        name = ''
        city = ''
        zc = ''
        state = ''
        lat = ''
        lng = ''
        store = ''
        country = 'US'
        HFound = False
        IsGas = False
        driver.get(loc)
        lines = driver.page_source.split('\n')
        for linenum in range(0, len(lines)):
            g = g
            g = str(g.decode('utf-8'))
            if 'Gas Hours</span>' in g:
                IsGas = True
                HFound = True
            if HFound and 'gas-price-section">' in g:
                HFound = False
            if HFound and '<time itemprop="openingHours" datetime="' in g:
                text = g.split('<time itemprop="openingHours" datetime="')[1].split('"')[0]
                if 'am' in text or 'pm' in text:
                    hrs = text.strip()
                    allhrs = day + ': ' + hrs
                else:
                    day = text.strip()
                    allhrs = ''
                if allhrs != '':
                    if hours == '':
                        hours = allhrs
                    else:
                        hours = hours + '; ' + allhrs
            if 'itemprop="latitude" content="' in g:
                lat = g.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in g:
                lng = g.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'data-identifier="' in g:
                store = g.split('data-identifier="')[1].split('"')[0]
            if '<h1' in g:
                name = g.split('<h1')[1].split('>')[1].split('<')[0].replace('&nbsp;',' ')
            if 'itemprop="streetAddress">' in g:
                add = g.split('itemprop="streetAddress">')[1].split('<')[0]
            if 'itemprop="addressLocality">' in g:
                city = g.split('itemprop="addressLocality">')[1].split('<')[0]
            if 'itemprop="addressRegion">' in g:
                state = g.split('itemprop="addressRegion">')[1].split('<')[0]
            if 'itemprop="postalCode">' in g:
                zc = g.split('itemprop="postalCode">')[1].split('<')[0]
            if phone == '' and 'itemprop="telephone">' in g:
                phone = g.split('itemprop="telephone">')[1].split('<')[0].strip().replace('\t','')
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if add != '' and IsGas is True:
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
