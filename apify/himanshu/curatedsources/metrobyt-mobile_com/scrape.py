import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import csv
import re
import json
import unicodedata
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","store_name","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=['US'])
    coord = search.next_coord()
    current_results_len = 0
    address = []
    json_data=0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'Content-Type': 'application/json',
        'Referer': 'https://www.bmwusa.com/?bmw=grp:BMWcom:header:nsc-flyout'
    }
    addressess = []

    while coord:
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        # print(search.current_zip)
        result_coords =[]
        
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
        }
        locator_domain = "https://www.metrobyt-mobile.com/"
        location_url = "https://www.metrobyt-mobile.com/api/v1/commerce/store-locator?address="+str(search.current_zip)+"&store-type=All&min-latitude="+str(coord[0])+"&max-latitude=37.0902&min-longitude="+str(coord[0])+"&max-longitude=-95.7129"
        r = session.get(location_url, headers=headers).json()

        for dt in r:
            
            # print(location_name)
            street_address = dt['location']['address']['streetAddress']
            zipp = dt['location']['address']['postalCode']
            state = dt['location']['address']['addressRegion']
            city = dt['location']['address']['addressLocality']
            latitude = dt['location']['latitude']
            longitude = dt['location']['longitude']
            phone = dt['telephone']
            hours_of_operation=''
            location_name=''
            for h in dt['openingHours']:
                hours_of_operation = ", ".join(h['days']) + ' ' + h['time']
            location_type=''
            location_type=dt['type']
            if location_type:
                if "Corporate Store" in location_type:
                    continue
            else:
                location_type=''
            page_url = ("https://www.metrobyt-mobile.com/storelocator/"+state.lower()+'/'+city.lower().replace(" ",'-')+'/'+street_address.lower().replace(" ",'-'))
            if len(zipp)==4:
                zipp = "0"+zipp

            
            if location_type:
                location_name = "Metro by T-Mobile "+location_type.strip()
            else:
                location_name =  'Amscot payment center'


            
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else 'Amscot payment center')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append('US')
            store.append('<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append("<MISSING>")
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(dt['name'] if dt['name'] else '<MISSING>')
            store.append(page_url)
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if str(store[2]+str(store[-7])+store[-1]) in addressess:
                continue
            addressess.append(str(store[2]+str(store[-7])+store[-1]))
            yield store
        
        if json_data < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif json_data== MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
