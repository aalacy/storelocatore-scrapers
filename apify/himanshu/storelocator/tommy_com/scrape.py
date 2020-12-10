import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tommy_com')


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
    }

    base_url = "https://www.tommy.com"
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=['US','CA'])
    MAX_RESULTS = 150
    MAX_DISTANCE = 100
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        data = '{"request":{"appkey":"0B93630E-2675-11E9-A702-7BCC0C70A832","formdata":{"geoip":false,"dataview":"store_default","limit":20,"geolocs":{"geoloc":[{"addressline":"'+str(zip_code)+'","country":"","latitude":"","longitude":"","state":"","province":"","city":"","address1":"","postalcode":""}]},"searchradius":"30|50|100|250","where":{"or":{"icon":{"like":""}}},"false":"0"}}}'
    
        r = session.post("https://hosted.where2getit.com/tommyhilfiger/rest/locatorsearch?like=0.8554840469970377", data=data, headers=headers).json()['response']
        if "collection" in r:
            current_results_len = len(r['collection'])
            for data in r['collection']:
                if "mall_name" in data:
                    location_name = data['mall_name']
                else:
                    location_name = "<MISSING>"
                street_address = (data['address1'] +" "+ str(data['address2'])).replace("None",'').strip()
                # logger.info(street_address)
                city = data['city']
                state = data['state']
                zipp = data['postalcode']
                # logger.info(zipp)
                country_code = data['country']
                if "clientkey" in data:
                    store_number = data['clientkey']
                else:
                    store_number = "<MISSING>"
                if "phone" in data:
                    phone = data['phone']
                else:
                    phone = "<MISSING>"
                if "googlecat1" in data:
                    location_type = data['googlecat1']
                else:
                    location_type = "<MISSING>"
                if "latitude" in data:
                    latitude = data['latitude']
                else:
                    latitude = "<MISSING>"
                if "longitude" in data:
                    longitude = data['longitude']
                else:
                    longitude = "<MISSING"
                if "mondayopen" in data:
                    hours = "Monday"+" "+ str(data['mondayopen']) +" "+"-"+" "+ str(data['mondayclose'])+ \
                        " "+ "Tuesday"+" "+ str(data['tuesdayopen']) +" "+"-"+" "+ str(data['tuesdayopen'])+ \
                        " "+ "Wednesday"+" "+ str(data['wednesdayopen']) +" "+"-"+" "+ str(data['wednesdayopen'])+ \
                        " "+ "Thursday"+" "+ str(data['thursdayopen']) +" "+"-"+" "+ str(data['thursdayopen'])+ \
                        " "+ "Friday"+" "+ str(data['fridayopen']) +" "+"-"+" "+ str(data['fridayopen'])+ \
                        " "+ "Saturday"+" "+ str(data['saturdayopen']) +" "+"-"+" "+ str(data['saturdayopen'])+ \
                        " "+ "Sunday"+" "+ str(data['sundayopen']) +" "+"-"+" "+ str(data['sundayopen']) 
                else:
                    hours = "<MISSING>"
                if state != None and store_number != None:
                    page_url = "https://stores.tommy.com/"+str(state.lower())+"/"+str(city.lower().replace(" ","-"))+"/"+str(store_number)+"/"
                else:
                    page_url = "<MISSING>"
                
                
                
                result_coords.append((latitude,longitude))
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country_code)
                store.append(store_number) 
                store.append(phone)
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours)
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                # logger.info("data ======="+str(store))
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store

        # logger.info("max count update")
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
