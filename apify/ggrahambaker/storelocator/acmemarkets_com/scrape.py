import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('acmemarkets_com')



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

    locator_domain = 'https://www.acmemarkets.com/'
    base_url = 'https://local.acmemarkets.com/'
    ext = 'index.html'
    r = session.get(base_url + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    links = soup.find_all('a', {'class': 'Directory-listLink'})

    state_list = []
    for li in links:
        state_list.append(base_url + li['href'])

    store_list = []
    more_stores = []
    for state in state_list:
        r = session.get(state, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        list_items = soup.find_all('li', {'class': 'Directory-listItem'})
        for li in list_items:
            link = base_url + li.find('a')['href']

            if len(link.split('/')) == 5:
                more_stores.append(link)
            else:
                store_list.append(link)

    for more in more_stores:
        r = session.get(more, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        links = soup.find_all('a', {'class': 'Teaser-titleLink'})
        
        for li in links:
            link = base_url + li['href'].replace('../', '')
            store_list.append(link)

    all_store_data = []
    for link in store_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        logger.info(link)

        lat = soup.find('meta', {'itemprop': 'latitude'})['content']
        longit = soup.find('meta', {'itemprop': 'longitude'})['content']
        location_name = soup.find('span', {'class': 'LocationName-geo'}).text
        city = soup.find('meta', {'itemprop': 'addressLocality'})['content']
        street_address = soup.find('meta', {'itemprop': 'streetAddress'})['content']
        
        state = soup.find('abbr', {'itemprop': 'addressRegion'}).text
        
        zip_code = soup.find('span', {'itemprop': 'postalCode'}).text
        
        phone_number = soup.find('div', {'id': 'phone-main'}).text
        
        data_days = soup.find('div', {'class': 'c-hours-details-wrapper'})['data-days']

        hours_json = json.loads(data_days)

        hours = ''
        for day in hours_json:
            hours += day['day'] + ' '
            interval = day['intervals'][0]

            start = str(interval['start'])
            end = str(interval['end'])
            if start == '0' and end == '0':
                hours += 'Open 24 Hours '
            else:
                start_time = start[:1] + ':' + start[-2:] + 'am'

                if end == '0':
                    end_time = '12:00 am'
                else:
                    end_time = end[:1] + ':' + end[-2:] + 'am'

                hours += start_time + ' - ' + end_time + ' '

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
