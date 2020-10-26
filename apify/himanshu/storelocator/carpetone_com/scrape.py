import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
import json
# import time



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    # zips = sgzip.for_radius(50)

    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["CA","US"])
    MAX_RESULTS = 25
    MAX_DISTANCE = 75.0
    coord = search.next_coord()
    current_results_len =0

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "application/json, text/plain, */*",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = "https://www.carpetone.com"
    locator_domain = "https://www.carpetone.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    while coord:
        # print("-------------------" + str(zip_code))
        result_coords =[]
        try:
            r = session.get('https://www.carpetone.com/carpetone/api/Locations/GetClosestStores?skip=0&zipcode=&latitude=' +
                         str(coord[0]) + '&longitude=' + str(coord[1]), headers=headers)
            # print('https://www.carpetone.com/carpetone/api/Locations/GetClosestStores?skip=0&zipcode=&latitude=' +str(coord[0]) + '&longitude=' + str(coord[1]))
        except:
            pass

        try:
            json_data = r.json()
            current_results_len = len(json_data)
        except:
            pass
        # print(json_data)

        for x in json_data:
            # try:
            ca_zip_list = re.findall(
                r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(x['Zip']))
            us_zip_list = re.findall(re.compile(
                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(x['Zip']))
            location_name = x['Name']
            street_address = x['Address']
            city = x['City']
            state = x['State']
            if us_zip_list:
                zipp = us_zip_list[0]
                country_code = "US"
            if ca_zip_list:
                zipp = ca_zip_list[0]
                country_code = "CA"
            #print(zipp)
            latitude = x['Latitude']
            longitude = x['Longitude']
            store_number = x['LocationNumber']
            url = x['MicroSiteURL']
            # print(url)
            if url != None:
                page_url = url
                #print("~~~~~~~~~~~~~~~~~~~~~~  ",page_url)
                try:
                    r_loc = session.get(page_url, headers=headers)
                except:
                    pass
                soup_loc = BeautifulSoup(r_loc.text, 'lxml')
                phone_tag = soup_loc.find('a', class_='phone-link')
                if phone_tag != None:
                    phone = phone_tag.text.replace('telephone', '').strip()
                else:
                    phone = "<MISSING>"
                hours_tag = soup_loc.find('ul', class_='store-hours')
                if hours_tag != None:
                    hr = []
                    for li in hours_tag.find_all('li'):
                        if "Call for Hours" not in li.text:
                            hr.append(li.text)
                        else:
                            hr.append("")
                    hours_of_operation = " ".join(hr).strip()
                else:
                    hours_of_operation = "<MISSING>"
            else:
                page_url = "<MISSING>"
                phone = "<MISSING>"
                hours_of_operation = "<MISSING>"

            store = []
            result_coords.append((latitude, longitude))
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(
                hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url if page_url else '<MISSING>')
            if store_number in addresses:
                continue
            addresses.append(store_number)
            # print("data====" + str(store))
            # print(
            #     "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
