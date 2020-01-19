import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 10
    current_results_len = 0    
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "http://dollargeneral.com"

    while zip_code:
        result_coords = []

        #print("zip_code === "+zip_code)
        data = '{"request":{"appkey":"9E9DE426-8151-11E4-AEAC-765055A65BB0","formdata":{"geoip":false,"dataview":"store_default","geolocs":{"geoloc":[{"addressline":"'+str(zip_code)+'","country":"US","latitude":"","longitude":""}]},"searchradius":"10|20|50|100","where":{"nci":{"eq":""},"and":{"PROPANE":{"eq":""},"REDBOX":{"eq":""},"RUGDR":{"eq":""},"MULTICULTURAL_HAIR":{"eq":""},"TYPE_ID":{"eq":""},"DGGOCHECKOUT":{"eq":""},"FEDEX":{"eq":""},"DGGOCART":{"eq":""}}},"false":"0"}}}'
        
        
        location_url = "http://hosted.where2getit.com/dollargeneral/rest/locatorsearch?like=0.9394142712975708"
        try:

            loc = requests.post(location_url,headers=headers,data=data).json()
        except:
            pass
      

        locator_domain = base_url
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

        hours_of_operation =''
       
        if "collection" in loc['response']:
            current_results_len = len(loc['response']['collection']) 
            for data in loc['response']['collection']:
                store_number = data['name'].split("#")[-1]
                
                hours_of_operation =' Monday '+ data['opening_time_mon']+ ' ' +data['closing_time_mon']+' Tuesday ' +data['opening_time_tue'] + ' ' +data['closing_time_tue'] + ' Wednesday ' + data['opening_time_wed'] + ' ' +data['closing_time_wed'] + ' Thursday ' + data['opening_time_thu'] + ' ' +data['closing_time_thu']+ ' Friday ' + data['opening_time_fri'] + ' ' +data['closing_time_fri']+ ' Saturday ' + data['opening_time_sat'] + ' ' +data['closing_time_sat']+ ' Sunday ' + data['opening_time_sun'] + ' ' +data['closing_time_sun']
                
                page_url = "<MISSING>"
                result_coords.append((latitude, longitude))
                store = [locator_domain, data['name'], data['address1'], data['city'], data['state'], data['postalcode'], country_code,
                        store_number, data['phone'], location_type, data['latitude'], data['longitude'], hours_of_operation,page_url]

                if store[2] + store[-3] in addresses:
                    continue

                addresses.append(store[2] + store[-3])
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                #print("data = " + str(store))
                #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                yield store
          

       
        if current_results_len < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
