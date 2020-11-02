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

def fetch_data():
    locator_domain = 'http://sharpeclothing.com/'
    ext = 'our-stores/'
    page = session.get(locator_domain + ext)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    names = soup.find_all('h3', {'class': 'post-name'})
    store_links = []
    for name in names:
        store_links.append(name.find('a')['href'])

    all_store_data = []
    for store in store_links:
        page = session.get(store)
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, 'html.parser')
        location_name = soup.find('h1', {'class': 'post-name'}).text
        store_info = soup.find('div', {'class': 'wp-block-column'})

        ps = store_info.find_all('p')
        br = ps[0].find('br')
        street_address = br.previousSibling
        city_state = br.nextSibling.split(',')

        city = city_state[0].replace('\n', '')
        state = city_state[1].strip()
        if len(state.split(' ')) == 2:
            arr = state.split(' ')
            state = arr[0]
            zip_code = arr[1]
        else:
            zip_code = '<MISSING>'

        phone_number = ps[1].find('a').text

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
