import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests


session = SgRequests()

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # driver = get_driver()
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.thrifty.com/"
    page = 1
    while True:

        page_url = "https://momentfeed-prod.apigee.net/api/llp.json?auth_token=EUQPBYIOEPTZLZLX&center=41.2524,-95.998&multi_account=false&page="+str(page)+"&pageSize=100"
        json_r = session.get(page_url, headers=headers).json()
        if 'message' in  json_r:
            break
        for data in json_r:
            
            if data['store_info']['status'] == "coming soon":
                continue
            street_address = data['store_info']['address']
            if data['store_info']['address_extended']:
                street_address = street_address +" "+ data['store_info']['address_extended']
            for locality in data['store_info']['providers']:
                if 'facebook_city' in locality:
                    
                    city = locality['facebook_city']
                    # print(page_url)
                    # print(data)
                    # print(city)
                    # print('==============================')
            state = data['store_info']['region']
            zipp = data['store_info']['postcode']
            country_code = data['store_info']['country']
            if country_code not in ['CA','US']:
                continue

            phone = data['store_info']['phone']
            latitude = data['store_info']['latitude']
            longitude = data['store_info']['longitude']
            location_name =data['store_info']['name']
            page_url = data['store_info']['website']
            store_number  = data['store_info']['corporate_id']
            location_type = data['store_info']['brand_name']
          

            # driver.get(page_url)
            # soup1 = BeautifulSoup(driver.page_source, "lxml")
            # try:
            #     hours = soup1.find("dl",{"class":"dl-horizontal"})['content']
            # except:
            #     hours = "<MISSING>"
           
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else"<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append("<INACCESSIBLE>")
            store.append(page_url if page_url else "<MISSING>")

            if store[2] in addresses:
                continue
            addresses.append(store[2])
            
            # print("data ==="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~``````")
            yield store 
        page+=1
        

    
        

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
