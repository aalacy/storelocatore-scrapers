import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time




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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 200
    # coord = search.next_coord()
    current_results_len = 0 
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        locator_domain = ''
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "CA"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        page_url = ""
        hours_of_operation = ""

        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        #print("zip_code === "+zip_code)
        # x = coord[0]
        # y = coord[1]
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        try:
            r = requests.get("https://www.insureone.com/locations/?address=" + str(zip_code) + "&search=search&page=1&radius=200",
                                "get", headers=headers)
                                
        except:
            continue
        soup = BeautifulSoup(r.text, 'lxml')
       
        ul = soup.find('ul', class_='office-locator-results__list')
        if ul != None:
            # print("len==" + len(ul))
            current_results_len = len( ul.find_all('li'))
            for li in ul.find_all('li'):
                base_url = "https://www.insureone.com/"
                store_number = "<MISSING>"
                locator_domain = base_url
                try:
                    location_name = li.find(
                        'h3', class_='office-locator-results__title').text.strip()
                except:
                    location_name =''
                
                try:
                    page_url = li.find(
                        'a', class_='office-locator-results__view')['href']
                except:
                    page_url =''


                try:   
                    r_loc = requests.get(page_url)
                    soup_loc = BeautifulSoup(r_loc.text, 'lxml')
                    script = soup_loc.find(
                        'script', {"type": "application/ld+json"}).text.strip()
                    json_data = json.loads(script)
                    location_type = json_data['@type'].strip()
                    phone = json_data['telephone'].strip()
                    street_address = json_data['address']['streetAddress']
                    city = json_data['address']['addressLocality']
                    state = json_data['address']['addressRegion']
                    zipp = json_data['address']['postalCode']
                    country_code = json_data['address']['addressCountry']
                    latitude = json_data['geo']['latitude']
                    longitude = json_data['geo']['longitude']
                    result_coords.append((latitude, longitude))
                    hours_of_operation = " ".join(json_data['openingHours']).replace('Mo', "MON :").replace('Tu', "TUE :").replace(
                        'We', "WED :").replace('Th', "THU :").replace('Fr', "FRI :").replace('Sa', "SAN :").replace('Su', "SUN :").strip()
                except:
                    pass

                store = []
                store.append(base_url)
                store.append(
                    location_name if location_name else "<MISSING>")
                store.append(
                    street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zip else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number if store_number else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append(
                    location_type if location_type else "<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(
                    hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                #print("===", str(store))
                #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                # return_main_object.append(store)
                yield store

               
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
    
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
