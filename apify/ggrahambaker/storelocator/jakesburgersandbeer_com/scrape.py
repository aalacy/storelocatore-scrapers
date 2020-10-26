import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jakesburgersandbeer_com')



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
    locator_domain = 'https://jakesburgersandbeer.com/' 
    ext = 'locations/'

    to_scrape = locator_domain + ext

    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')
    rows = soup.find_all('div', {"class": "location-row"})
    all_store_data = []

    for row in rows:
        content = row.find('div', {'class': 'col-sm-10'})
        
        location_name = content.find('h3').text
        
        addy = content.find('p', {'class': 'street-address'})
        
        addy_arr =  addy.text.strip().split('\n')
        street_address = addy_arr[0]
        addy_info = addy_arr[1].replace('\t\t\t\t\t\t\t\t\t\t\t\t', '')
        
        addy_info_split = addy_info.split(',')
        city = addy_info_split[0]
        addy_info_rest = addy_info_split[1].split(' ')
        
        state = addy_info_rest[1]
        zip_code = addy_info_rest[2]
        
        hours_temp = content.find('p', {'class': 'hours'})
        # logger.info(hours_temp.text.strip().split('\n'))
        hours = ''
        for hour in hours_temp.text.strip().split('\n'):
            h = hour.replace('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t', '')
            hours += h + ' '
            
        # logger.info(hours)
        phone_temp = content.find('p', {'class': 'phone'})
        #logger.info(phone_temp.text.strip())
        phone_number = phone_temp.text.strip()
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = 'resturant'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                 store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
