import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('shopatgrants_com')



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

    locator_domain = 'https://shopatgrants.com/' 
    ext = 'stores/'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    stores = soup.find_all('p')

    # dont do the last one or the first one!
    all_store_data = []
    for store in stores[1:-2]:
      # easy case
        if len(store.text.strip().split('\n')) > 1:
            store_info = store.text.strip().split('\n')
            location_name = store_info[0].strip()
            street_address = store_info[0].strip()
            
            addy_info = store_info[1].strip().split(' ')
            # there might be trailing comma
            city = ''
            state = ''
            for addy in addy_info:
                if addy.isupper() and len(addy) == 2:
                    state = addy
                    #logger.info(state)
                    break
                else:
                    city += addy + ' '
                    #logger.info(city)
            #city = addy_info[0].replace(',','')
            #state = addy_info[1]
            
            city = city.replace(',','')
            
            phone = store_info[2].strip()
            
            if len(store_info) == 4:
                hours = store_info[3]
            else:
                hours = store_info[3] + ' ' + store_info[4]
                
        # hard case, all together
        else:
            text = store.text
            last = ''
            for i, c in enumerate(text):
                if c.isupper() and last.islower():
                    ## found first split!
                    split_index = i
                last = c
                
            #logger.info(split_index)
            #logger.info(text[:split_index])
            location_name = text[:split_index]
            street_address = text[:split_index]
            
            addy_info_cut = text[split_index:].index('WV')
            city = text[split_index:][:addy_info_cut]
            state = text[split_index:][addy_info_cut:addy_info_cut+2]
            
            phone_and_hours = text[split_index:][addy_info_cut+2:]

            phone_number = phone_and_hours[:12]
        
            hours = phone_and_hours[12:]
        
        country_code = 'US'
        zip_code = '<MISSING>'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        long = '<MISSING>'
        
        # done parsing, lets push it to an array
        # should be like this
        # locator_domain, location_name, street_address, city, state, zip, country_code,
        # store_number, phone, location_type, latitude, longitude, hours_of_operation
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, long, hours ]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
