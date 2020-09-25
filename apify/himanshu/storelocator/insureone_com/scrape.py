import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',newline ="") as output_file:
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
    MAX_RESULTS = 100
    MAX_DISTANCE = 200
    # coord = search.next_coord()
    current_results_len = 0 
    zip_code = search.next_zip()
    while zip_code:
        # print(search.current_zip)
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('============================')
        base_url = "https://www.insureone.com/"
        result_coords = []
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = ""
        store_number = "<MISSING>"
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        page_url = ""
        hours_of_operation = ""
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        #print("zip_code === "+zip_code)
        # x = coord[0]
        # y = coord[1]
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        data = {"address": ""+str(zip_code)+"",
                "search": "search",
                "page": "1",
                "radius": "200"}
        r = session.post("https://www.insureone.com/locations/",data=data,headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        ul = soup.find('ul', class_='office-locator-results__list')
        if ul != None:
            current_results_len= len(ul)
            # current_results_len = len(ul.find_all('li'))
            for li in ul.find_all('li'):
                try:
                    location_name = li.find('h3', class_='office-locator-results__title').text.strip()
                    page_url = li.find('h3', class_='office-locator-results__title').find("a")["href"]
                    r_loc = session.get(page_url)
                    soup_loc = BeautifulSoup(r_loc.text, 'html5lib')
                    script = soup_loc.find('script', {"type": "application/ld+json"}).text.strip()
                    json_data = json.loads(script)
                    location_type = json_data['name'].strip()
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
                    
                    store = [locator_domain, location_name.replace(': Maps',''), street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                    if str(store[1] + " "+ store[2]+ " "+ store[9]) not in addresses and country_code:
                        addresses.append(str(store[1] + " "+ store[2]+ " "+ store[9]))

                        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                        # print("data = " + str(store))
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        yield store
                except:
                    continue
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
