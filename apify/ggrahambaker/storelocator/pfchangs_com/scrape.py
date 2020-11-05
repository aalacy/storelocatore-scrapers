import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pfchangs_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.pfchangs.com/'
    ext = 'locations/'
    r = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    hrefs = soup.find_all('a', {'class': 'Directory-listLink'})

    state_link_list = []
    loc_link_list = []
    for href in hrefs:
        link = locator_domain + ext + href['href']
        if len(link) > 45:
            loc_link_list.append(link)
        else:
            state_link_list.append(link)

    city_link_list = []
    for state in state_link_list:

        r = session.get(state, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        hrefs = soup.find_all('a', {'class': 'Directory-listLink'})
        for href in hrefs:
            link = locator_domain + ext + href['href'].replace('../', '')
            if len(link.split('-')) > 3:
                loc_link_list.append(link)
            else:
                city_link_list.append(link)
    for city in city_link_list:
        r = session.get(city, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        locs = soup.find_all('a', {'class': 'Teaser-titleLink'})

        for loc in locs:
            link = locator_domain + ext + loc['href'].replace('../', '')
            loc_link_list.append(link)

    all_store_data = []
    for link in loc_link_list:

        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        location_name = soup.find_all('span', {'id': 'location-name'})
        if len(location_name) != 1:
            continue
        location_name = location_name[0].text
        
        street_address = soup.find('span', {'class': 'c-address-street-1'}).text
        
        if len(soup.find_all('span', {'class': 'c-address-street-2'})) == 1:
            street_address += ' ' + soup.find('span', {'class': 'c-address-street-2'}).text

        city = soup.find('span', {'class': 'c-address-city'}).text.replace(',', '').strip()
        
        state = soup.find('abbr', {'class': 'c-address-state'}).text
        
        zip_code = soup.find('span', {'class': 'c-address-postal-code'}).text

        phone_number = soup.find('div', {'id': 'phone-main'}).text

        coords = soup.find('meta', {'name': 'geo.position'})['content'].split(';')
        lat = coords[0]
        longit = coords[1]

        country_code = 'US'
        page_url = link
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        
        hours_td = soup.find('div', {'class': 'js-hours-table'})['data-days']
        hours_json = json.loads(hours_td)
        hours = ''
        for h in hours_json:
            day = h['day']
            if len(h['intervals']) == 0:
                hours += day + ' Closed '
            else:
                start = h['intervals'][0]['start']
                end = h['intervals'][0]['end']

                hours += day + ' ' + str(start) + ' - ' + str(end) + ' '

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        logger.info(store_data)
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
