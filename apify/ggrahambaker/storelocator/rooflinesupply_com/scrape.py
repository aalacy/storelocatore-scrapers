import csv
import requests
from bs4 import BeautifulSoup


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

    locator_domain = 'http://rooflinesupply.com/'
    to_scrape = locator_domain
    page = requests.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    stores = soup.find_all('div', {'class': 'locations'})
    all_store_data = []


    for store in stores:    
        location_name = store.find('a').text
        phone_number = store.find_all('a', {'title': 'Phone'})[0].text
        
        brs = store.find_all('br')
        street_address = brs[0].nextSibling.strip()
        city, state, zip_code = addy_extractor(brs[1].nextSibling.strip())

        hr_brs = brs[1:]
        hours = hr_brs[4].previousSibling.strip()
        if hours == '':
            hours = '<MISSING>'
        else:
            if hr_brs[5].previousSibling.strip() == 'CLOSED':
                hours += ' CLOSED WEEKENDS'
            else:
                hours += ' ' + hr_brs[5].previousSibling.strip()
            
            
        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
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
