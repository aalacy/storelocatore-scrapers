# coding=UTF-8
import csv
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
import requests
from concurrent.futures import ThreadPoolExecutor

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
                # print(data.text)

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
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
    # list_of_urls.append( "{\"r\":\"1000\",\"zip\":%s,\"requestType\":\"dotcom\",\"s\":\"1000\"}"%('"{}"'.format(str(85029))))
    while zip_code:
        result_coords = []
        # print(zip_code)
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print("https://us.nissan-api.net/v2/dealers?size=50&isMarketingDealer=true&location="+str(zip_code)+"&serviceFilterType=AND&include=openingHours")
        
        list_of_urls.append("https://us.nissan-api.net/v2/dealers?size=50&isMarketingDealer=true&location="+str(zip_code)+"&serviceFilterType=AND&include=openingHours")  

        # if len(list_of_urls)==2:
        #     break
        
              
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()

    #print("len---- ",len(list_of_urls))
    data = _send_multiple_rq(list_of_urls)
    for q in data:
        # print(q)
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
                hours =''
                day=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
                for h in location["openingHours"]['regularOpeningHours']:

                    weekDay=day[h['weekDay']-1]
                    if "openIntervals" in h:
                        for q in h['openIntervals']:
                            hours +=' ' +weekDay+' open '+q['openFrom']+' colse '+ q['openUntil']
                    else:
                        hours += ' ' +day[h['weekDay']-1]+ ' '+"closed"
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
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # print("data =="+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
