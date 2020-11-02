import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1].replace('.', '')
        zip_code = prov_zip[2]

    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://costlessfoods.com/'
    ext = 'locations/'

    page = session.get(locator_domain + ext)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    divs = soup.find_all('div', {'class': 'margins'})
    coords = soup.find_all('div', {'class': 'dooMapLatLong'})

    all_store_data = []

    for i, div in enumerate(divs):
        full = div.find('h4').text.strip()

        location_name = div.find('h4').text.strip().split(':')[1].strip()

        idx = full.find('#')
        colon = full.find(':')
        store_number = full[idx + 1:colon]
        brs = div.find('p', {'class': 'theme_style'}).find_all('br')

        phone_number = brs[0].nextSibling
        street_address = brs[4].nextSibling
        city, state, zip_code = addy_extractor(brs[5].nextSibling)
        hours = brs[-1].nextSibling

        country_code = 'US'
        location_type = '<MISSING>'

        coord = coords[i].text.replace('\t', '').replace('\r', '')

        split = coord.split(',')
        lat = split[0]
        longit = split[1]

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
