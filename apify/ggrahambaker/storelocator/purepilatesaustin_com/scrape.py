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
    locator_domain = 'https://www.purepilatesaustin.com/'
    ext = 'locations'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')
    stores = soup.find_all('div', {'class': 'blockText'})
    all_store_data = []

    for store in stores[1:-2]:
        location_name = store.find('h2').text.strip()
        a_tag = store.find_all('a')[0]

        addy_arr = a_tag.text.split(',')
        street_address = addy_arr[0]
        city = addy_arr[1]
        addy_arr2 = addy_arr[2].split(' ')
        state = 'TX'
        zip_code = addy_arr2[2]
        g_map_link = a_tag['href'].split('@')[1].split(',')
        lat = g_map_link[0]
        longit = g_map_link[1]
        phone_number = store.find_all('a')[1]
        if not phone_number.text[0].isdigit():
            phone_number = phone_number.previousSibling.replace('//', '').strip()
        else:
            phone_number = phone_number.text
            
        country_code = 'US'
        store_number = '<MISSING>'
        hours = '<MISSING>' 
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
