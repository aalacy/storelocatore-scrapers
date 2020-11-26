import csv
from bs4 import BeautifulSoup
import sgzip
import re
import json
# import unicodedata
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('waitrose_com')


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes = ["UK"])
    MAX_RESULTS = 500
    MAX_DISTANCE = 1
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    addresses = []
    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # logger.info(search.current_zip)
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        base_url = "https://www.waitrose.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36,'
        }
        try:
            json_data = session.get("https://www.waitrose.com/shop/NearestBranchesCmd?latitude="+str(lat)+"&longitude="+str(lng)+"&fromMultipleBranch=true&_=1585897775137",headers=headers ).json()['branchList']
        except:
            search.max_distance_update(MAX_DISTANCE)
            coord = search.next_coord()
            # continue
        current_results_len = len(json_data)
        for data in json_data:
            location_name = data['branchName']
            street_address = data['addressLine1'].replace("&#039;","'").strip()
            city = data['city']
            zipp = data['postCode']
            phone = data['phoneNumber']
            # phone = phonenumbers.format_number(phonenumbers.parse("8174842005", 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
            store_number = data['branchId']
            latitude = data['latitude']
            longitude = data['longitude']
            page_url = "https://www.waitrose.com/content/waitrose/en/bf_home/bf/"+str(store_number)+".html"
            # logger.info(page_url)
            r1 = session.get(page_url,headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            # addr = soup1.find("div",{"class":"col branch-details"}).text.replace(street_address,"").replace(city,"").replace(zipp,"").replace(phone,"").strip()
            try:
                hours_of_operation = " ".join(list(soup1.find("table").stripped_strings))
            except:
                hours_of_operation = "<MISSING>"

            result_coords.append((latitude,longitude))
            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append("<INACCESSIBLE>")
            store.append(zipp if zipp else "<MISSING>")   
            store.append("UK")
            store.append(store_number if store_number else "<MISSING>") 
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if (store[1]+store[2]+store[-1]) in addresses:
                    continue
            addresses.append(store[1]+store[2]+store[-1])
            # for i in range(len(store)):
            #     if type(store[i]) == str:
            #         store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            # store = [str(x).replace("\xe2","-").replace("\xe7",'') if x else "<MISSING>" for x in store]
            # store = [unidecode.unidecode(x).strip() if x else "<MISSING>" for x in store]
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store
            # logger.info(store)
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
