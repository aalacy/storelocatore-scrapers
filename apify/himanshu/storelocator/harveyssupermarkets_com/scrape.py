import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('harveyssupermarkets_com')




session = SgRequests()

def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url, headers=headers, data=data)
                else:
                    r = session.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None



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
    addresess = []
    MAX_RESULTS = 50
    MAX_DISTANCE = 25
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    zip_code = search.next_zip()
    current_results_len =0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.harveyssupermarkets.com',
        'Referer': 'https://www.harveyssupermarkets.com/Locator',
    }
    while zip_code: 
        result_coords = []
        # logger.info("zip_code === "+zip_code)
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        data = "fhController=ContentComponentsController&fhAction=StoreLocatorResults&sitename=harveys&bannerName=Harveys+Supermarket+%23+&CurrentState=StrTab&StoreZipCode="+str(zip_code)+"&MilesSelectedValue=25&MilesSelectedValue=25&strCommand=Search&ATM=false&Floral=false&Lottery=false&RedBox=false&CoinCounter=false&FreshMeat=false&MTMO=false&SeaFood=false&DeliBakery=false&GlutenFree=false&Pharmacy=false&Sushi=false&ATM=false&Floral=false&Lottery=false&RedBox=false&CoinCounter=false&FreshMeat=false&MTMO=false&SeaFood=false&DeliBakery=false&GlutenFree=false&Pharmacy=false&Sushi=false"
  
        r = request_wrapper("https://www.harveyssupermarkets.com/Locator",'post',headers=headers,data=data)

        soup = BeautifulSoup(r.text, "lxml")
        info = soup.find_all("a",{"class":"store-details storeLink"})
        current_results_len = len(info)
        for i in info:
            href = "https://www.harveyssupermarkets.com"+str(i['href'])
 
            r1 = request_wrapper(href,'get',headers=headers)  

            soup1 = BeautifulSoup(r1.text, "lxml")
            info1 = soup1.find_all("div",{"class":"row storeDetailsRow"})[-1]
            info2 = soup1.find_all("script")
            hours = list(info1.stripped_strings)
            hours_of_operation = ''.join(hours[1:4])
            
            for j in info2:
                if "var locations  =" in j.text:
                    data =j.text.split("var locations  =")[1].split(";")[0]
                    street_address = ''.join(json.loads(data)[0][0].split(',')[:-2])
                    city= json.loads(data)[0][0].split(',')[-2]
                    state = json.loads(data)[0][0].split(',')[-1].split(' ')[1]
                    zip1 = json.loads(data)[0][0].split(',')[-1].split(' ')[2]
                    latitude = json.loads(data)[0][1]
                    longitude = json.loads(data)[0][2]
                    phone = json.loads(data)[0][7]
                    store_number = json.loads(data)[0][3]
                    location_name = json.loads(data)[0][11]


                    store = []
                    result_coords.append((latitude, longitude))
                    store.append("https://www.harveyssupermarkets.com")
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city.replace('\n',''))
                    store.append(state)
                    store.append(zip1)   
                    store.append("US")
                    store.append(store_number)
                    store.append(phone)
                    store.append("<MISSING>")
                    store.append(latitude )
                    store.append(longitude )
                    store.append(hours_of_operation)
                    store.append(href)
                    if store[2] in addresess:
                        continue     
                    addresess.append(store[2])
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
