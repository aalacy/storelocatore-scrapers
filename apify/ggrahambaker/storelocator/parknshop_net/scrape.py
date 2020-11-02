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
    locator_domain = 'https://www.parknshop.net/' 
    ext = 'park-n-shop-locations/'

    to_scrape = locator_domain + ext

    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    panel = soup.find_all('div', {'class':'panel-grid'})

    all_store_data = []

    cycle = [1, 3, 5] 
    for i in cycle:
        ps = panel[i].find_all('p')
        location_name = ps[1].text
        street_address = ps[2].text
        addy_info = ps[3].text.split(',')
        city = addy_info[0]
        addy_info2 = addy_info[1].split(' ')
        state = addy_info2[1]
        zip_code = addy_info2[2]
        
        hours = ps[5].text + ' ' + ps[6].text
        phone_number = ps[7].text.replace('Phone Number:', '').strip()
        
        country_code = 'US'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                         store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
