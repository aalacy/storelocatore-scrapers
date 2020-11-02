import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jiffytrip_com')



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
    locator_domain = 'http://jiffytrip.com/' 
    ext = 'locations'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)

    assert page.status_code == 200
    
    soup = BeautifulSoup(page.content, 'html.parser')

    body = soup.find('div', {'class': 'stack'})
    divs = body.find_all('div', {"class": "row"})

    all_store_data = []

    for div in divs[1:]:
        #location_name = div
        cols = div.find_all('div')
        #logger.info(cols)
        store_number = cols[0].text
        location_name = cols[2].text
        street_address = cols[2].text
        city = cols[3].text
        zip_code = cols[4].text
        phone_number = cols[5].text
        state = 'OK'
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)    

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
