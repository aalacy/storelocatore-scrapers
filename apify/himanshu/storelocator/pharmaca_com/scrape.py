import csv
from sgrequests import SgRequests
import json
from datetime import timedelta
from datetime import datetime
from bs4 import BeautifulSoup
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():

    
    locator_domain_json = 'https://www.pharmaca.com/amlocator/index/ajax/'
    r = session.get("https://www.pharmaca.com/store-locator")
    soup = BeautifulSoup(r.text,"html.parser")
    
    data = soup.find(lambda tag: (tag.name == "script" or tag.name == "h2") and "jsonLocations" in tag.text.strip()).text.split("jsonLocations:")[1].split("imageLocations:")[0].strip()[:-1]
    data = (json.loads(data))
    # exit()
    # an_obj = session.get("https://www.pharmaca.com/store-locator")

    # driver = get_driver()
    # driver.get(locator_domain + ext)
    
    all_store_data = []
    for obj in data['items']:
        page_url = "https://www.pharmaca.com"+obj['website']
        store_number = '<MISSING>'
        location_name = obj['name']
        country_code = obj['country']
        city = obj['city']
        zip_code = obj['zip']
        if 'Santa' in zip_code:
            zip_code = '<MISSING>'
        state = obj['state']
        street_address = obj['address']
        # print(street_address)
        lat = obj['lat']
        longit = obj['lng']
        phone_number = obj['phone']
        location_type = '<MISSING>'
        to_make = json.loads(obj['schedule'])
        hours1 = json.loads((obj['schedule_string']))
        hours_of =''
        for h in  hours1:
            hours_of = hours_of+ ' ' +( h + ' open ' + hours1[h]['from']['hours']+ ' close '+ hours1[h]['to']['hours'])

        locator_domain = 'https://www.pharmaca.com/'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours_of,page_url]
        yield store_data
  
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
