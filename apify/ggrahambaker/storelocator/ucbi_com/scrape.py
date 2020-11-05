import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ucbi_com')



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

    locator_domain = 'https://www.ucbi.com/' 
    ext = 'locations/'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find('div', {'class': 'locations-listings'}).find_all('article')

    all_store_data = []

    for loc in locs:
        location_name = loc['aria-label']
        
        lat = loc['data-lat']
        longit = loc['data-lng']
        
        loc_types = loc.find('div', {'class': 'options'}).find_all('div')
        location_type = ''
        for t in loc_types:
            location_type += t.text + ' '
            
        phone_number = loc.find('div', {'class': 'locationContact'}).find('a').text
        
        page_url = locator_domain[:-1] + loc.find('a')['href']

        r = session.get(page_url, headers = HEADERS)

        soup = BeautifulSoup(r.content, 'html.parser')

        addy = soup.find('p', {'itemprop': 'streetAddress'})

        street_city = addy.find_all('span', {'itemprop': 'addressLocality'})
        street_address = street_city[0].text
        city = street_city[1].text

        state = addy.find('span', {'itemprop': 'addressRegion'}).text
        zip_code = addy.find('span', {'itemprop': 'postalCode'}).text
  
        office_hours = soup.find_all('ul', {'itemprop': 'openingHoursSpecification'})

        if len(office_hours) == 0:
            hours = '<MISSING>'
        else:
            days = office_hours[0].find_all('li')
            hours = 'Office Hours : '
            for day in days:
                hours += day.text.strip() + ' '

        store_number = '<MISSING>'
        country_code = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        logger.info(store_data)
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
