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
    # return 2D array to be written to csv
    locator_domain = 'https://holtzmancorp.com/'

    to_scrape = locator_domain
    page = session.get(to_scrape)
    soup = BeautifulSoup(page.content, 'html.parser')
    div = soup.find('div', {"id": "pl-w5cfeac7473594"})
    panel = div.find_all('div', {'class': 'panel-grid-cell'})
    
    all_store_data = []

    oil_divs = [panel[2], panel[3], panel[4]]

    for div in oil_divs:
        ps = div.find_all('p')
        location_name = ps[0].text
        street_address = ps[0].text
        addy_info_arr = ps[1].text.split(',')
        city = addy_info_arr[0]
        state = addy_info_arr[1].split(' ')[1]
        zip_code = addy_info_arr[1].split(' ')[2]
        phone_number = ps[2].text
        country_code = 'US'
        location_type = 'oil'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        store_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    propane_divs = [ panel[7], panel[8], panel[9], panel[10]]
    for div in propane_divs:
        ps = div.find_all('p')
        location_name = ps[0].text
        street_address = ps[0].text
        addy_info_arr = ps[1].text.split(',')
        city = addy_info_arr[0]
        state = addy_info_arr[1].split(' ')[1]
        zip_code = addy_info_arr[1].split(' ')[2]
        phone_number = ps[2].text
        country_code = 'US'
        location_type = 'propane'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        store_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
