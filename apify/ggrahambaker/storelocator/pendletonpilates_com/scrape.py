import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

  
## helpter  
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]
    
    
    return [city, state, zip_code]


def fetch_data():
    locator_domain = 'http://www.pendletonpilates.com/' 
    ext = 'our-locations'

    to_scrape = locator_domain + ext

    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')
    div = soup.find('div', {'id': 'page-548a13a6e4b01aa5bebe2534'})
    stores = div.find_all('div', {'class': 'row sqs-row'})
    
    all_store_data = []   


    for store in stores[1:]:
        location_name = store.find('h3').text.upper()
        

        json_data = json.loads(store.find('div', {'class':'sqs-block'})['data-block-json'])
        
        lat = json_data['location']['markerLat']
        longit = json_data['location']['markerLng']
        
        p = store.find('h3').nextSibling
        p_brs = p.find_all('br')
        if len(p_brs) == 3:
            street_address = p_brs[0].previousSibling
            addy = addy_extractor(p_brs[1].previousSibling)
            city = addy[0]
            state = addy[1]
            zip_code = addy[2]
            phone_number = p_brs[2].previousSibling
        else:
            street_address = p_brs[0].previousSibling
            addy = addy_extractor(p_brs[2].previousSibling)
            city = addy[0]
            state = addy[1]
            zip_code = addy[2]
            phone_number = p_brs[3].previousSibling
            
        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        hours = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
