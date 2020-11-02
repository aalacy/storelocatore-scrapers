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

#helper for getting address
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]
    
    return city, state, zip_code

def fetch_data():

    locator_domain = 'http://www.pink-barre.com/'

    ext = 'locations'
    to_scrape = locator_domain + ext

    page = session.get(to_scrape)

    soup = BeautifulSoup(page.content, 'html.parser')
    divs = soup.find_all('div', {'class': 'sqs-block-content'})
    all_store_data = []

    loc_i = [0, 1]
    for i in loc_i:
        location_name = divs[i].find('h2').text
        br = divs[i].find_all('p')[0].find('br')
        street_address = br.previousSibling.text

        city, state, zip_code = addy_extractor(br.nextSibling)
       
        phone_number = divs[i].find_all('p')[1].text.strip()
        hours = divs[i].find_all('p')[2].text + ' ' + divs[i].find_all('p')[3].text
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        
        all_store_data.append(store_data)
        
    location_name = divs[4].find('h2').text
    br = divs[4].find_all('p')[1].find('br')
    street_address = br.previousSibling.text
    city, state, zip_code = addy_extractor(br.nextSibling)
    phone_number = divs[4].find_all('p')[2].text.strip()
    hours = '<MISSING>'
    country_code = 'US'
    store_number = '<MISSING>'
    location_type = '<MISSING>'
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
