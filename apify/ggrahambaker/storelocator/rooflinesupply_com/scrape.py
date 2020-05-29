import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

# helper for getting address
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]

    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://rooflinesupply.com/'
    to_scrape = locator_domain
    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')
    pattern = re.compile('(([\-\+]{0,1}\d[\d\.\,]*[\.\,][\d\.\,]*\d+)\,\s+([\-\+]{0,1}\d[\d\.\,]*[\.\,][\d\.\,]*\d+))')
    pair_pattern = re.compile('((\w+)=\"([^\"]+)\")')

    script = soup.find('script', text=pattern)

    results_locs = re.findall(pair_pattern, script.text)
    loc_arr = []
    for i, res in enumerate(results_locs):
        if 'title' in res:
            res = str(res)
            idx = [i.start() for i in re.finditer('"', res)]
            loc_arr.append([res[idx[0] + 1:idx[1]]])

    results = re.findall(pattern, script.text)
    for i, loc in enumerate(loc_arr):
        loc.append(results[i][0])

    stores = soup.find_all('div', {'class': 'locations'})
    all_store_data = []

    for store in stores:
        location_name = store.find('a').text
        phone_number = store.find_all('a', {'title': 'Phone'})[0].text

        brs = store.find_all('br')
        street_address = brs[0].nextSibling.strip()
        city, state, zip_code = addy_extractor(brs[1].nextSibling.strip())

        hr_brs = brs[1:]
        hours = hr_brs[4].previousSibling.strip()
        if hours == '':
            hours = '<MISSING>'
        else:
            if hr_brs[5].previousSibling.strip() == 'CLOSED':
                hours += ' CLOSED WEEKENDS'
            else:
                hours += ' ' + hr_brs[5].previousSibling.strip()

        for loc in loc_arr:
            if city in loc[0]:
                coords = loc[1].split(',')
                lat = coords[0]
                longit = coords[1]

        if '4350 Pell Drive, Ste 100' in street_address:
            lat = '38.647544'
            longit = '-121.469982'

        if '5870 88th Street' in street_address:
            lat = '38.520273'
            longit = '-121.376846'

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
