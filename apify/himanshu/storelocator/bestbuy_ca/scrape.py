import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bestbuy_ca')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!    
    search.initialize(include_canadian_fsas = True)
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url= "https://bestbuy.ca"
    while zip_code:
        result_coords = []
        headers = {   
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',        
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'accept': 'application/json'
        }   
        try:
            r = session.get("https://stores.bestbuy.ca/en-ca/search?q="+str(zip_code), headers=headers).json()
        except :
            pass
        current_results_len = len(r['locations'])
        for i in range(len(r['locations'])):
            street_address = r['locations'][i]['loc']['address1']+" "+r['locations'][i]['loc']['address2']
            if "3401 Dufferin St., Unit 303" in street_address:
                continue
            city =  r['locations'][i]['loc']['city']  
            state = r['locations'][i]['loc']['state']
            zipp = r['locations'][i]['loc']['postalCode']
            store_number = r['locations'][i]['loc']['corporateCode']
            phone = r['locations'][i]['loc']['phone']
            country_code = r['locations'][i]['loc']['country']
            latitude = r['locations'][i]['loc']['latitude']
            longitude = r['locations'][i]['loc']['longitude']
            page_url = "https://stores.bestbuy.ca/"+r['locations'][i]['url']
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            location_name = soup1.find("span",{"class":"LocationName"}).text.strip()
            hours = r['locations'][i]['loc']['hours']['days']
            drive_hours = ''
            for day in hours:
                for interval in day['intervals']:           
                    value_starttime = datetime.strptime(str(interval['start']), "%H%M")
                    starttime= value_starttime.strftime("%I:%M %p")
                    value_endtime = datetime.strptime(str(interval['end']), "%H%M")
                    endtime= value_endtime.strftime("%I:%M %p")
                    drive_hours = drive_hours+" "+day['day'].capitalize() +" "+str(starttime)+"-"+str(endtime)
            hours_of_operation = drive_hours
            store = []
            result_coords.append((latitude, longitude))
            store.append(base_url)
            store.append(location_name)
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append('<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url if page_url else '<MISSING>')
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # logger.info("data =="+str(store))
            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
       
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
