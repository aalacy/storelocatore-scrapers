# coding=UTF-8
import csv
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('infiniti_ca')



def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        
        for row in data:
            writer.writerow(row)


def get_url(data):

    headers = {
    'Accept': '*/*',
    'clientKey': 'lVqTrQx76FnGUhV6AFi7iSy9aXRwLIy7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    'apiKey': 'mKvJTEihQ3gYy0GhoYKWrAbKfzWt3PsE'
    }

    data = requests.get(data,headers=headers)
    try:
        return data
    except:
        pass

def _send_multiple_rq(vk):
    with ThreadPoolExecutor(max_workers=len(vk)) as pool:
        # for data in list(pool.map(get_url,list_of_urls)):
        return list(pool.map(get_url,vk))
                # logger.info(data.text)

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=["CA"])
    MAX_RESULTS = 1000
    MAX_DISTANCE =10
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()
    headers = {
    'Accept': '*/*',
    'clientKey': 'lVqTrQx76FnGUhV6AFi7iSy9aXRwLIy7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    'apiKey': 'mKvJTEihQ3gYy0GhoYKWrAbKfzWt3PsE'
    }

    base_url = "https://www.infiniti.ca"
    list_of_urls=[]
    while zip_code:
        result_coords = []
        # logger.info(zip_code)
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))        
        list_of_urls.append("https://us.nissan-api.net/v2/dealers?size=50&isMarketingDealer=true&location="+str(zip_code)+"&serviceFilterType=AND&include=openingHours")  
        # if len(list_of_urls)==5:
        #     break
              
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()

    #logger.info("len---- ",len(list_of_urls))
    data = _send_multiple_rq(list_of_urls)
    for q in data:
        # logger.info(q)
        r1= q.json()
        if "dealers" in  r1:
            locator_domain = "https://www.infiniti.ca/"
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = "US"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            raw_address = ""
            hours_of_operation = ""
            for location in r1["dealers"]:
                storeNumber = "<MISSING>"
                location_name = location['name']
                phone =location['contact']['phone']
                storeNumber = "<MISSING>"
                latitude = location['geolocation']['latitude']
                longitude = location['geolocation']['longitude']
                zipp = location['address']['postalCode']
                if zipp.replace("-","").strip().isdigit():
                    country_code = "US"
                else:
                    country_code = "CA"
                if phone.strip().lstrip():
                    phone = phone
                else:
                    phone = "<MISSING>"  
                page_url = location['contact']['websites'][0]['url']
                hours_of_operation =''
                day=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
                for h in location["openingHours"]['regularOpeningHours']:
                    if "openIntervals" in h:
                        weekDay=day[h['weekDay']-1]
                        for q in h['openIntervals']:
                            hours_of_operation +=' ' +weekDay+' open '+q['openFrom']+' colse '+ q['openUntil']
                    else:
                        weekDay=day[h['weekDay']-1]
                        hours_of_operation += ' ' +day[h['weekDay']-1]+ ' '+"closed"
                # logger.info(hours_of_operation)
                # try:
                #     r1 = requests.get(page_url ,headers=headers)
                # except:
                #     pass
                # soup = BeautifulSoup(r1.text,"lxml")
                # try:
                #     hours_of_operation = " ".join(list(soup.find("div",{"class":'service-section'}).find("li",{"class":'single-hours-lists'}).stripped_strings))
                # except:
                # hours_of_operation =hours

                store = [locator_domain, location_name, location['address']['addressLine1'], location['address']['city'].capitalize(), location['address']['state'], zipp, country_code,
                        storeNumber, phone.strip(), location_type, latitude, longitude, hours_of_operation,page_url.lower()]

                if str(store[2]) in addresses:
                    continue
                addresses.append(str(store[2]) )
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                # logger.info("data =="+str(store))
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
