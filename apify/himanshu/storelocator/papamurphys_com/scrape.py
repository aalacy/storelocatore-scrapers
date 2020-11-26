import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0   
    zip_code = search.next_zip()
    headers = {
        'authority': 'order.papamurphys.com',
        'method': 'GET',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
       'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,gu;q=0.8',
        'cache-control': 'max-age=0.',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    }
    base_url = "https://www.papamurphys.com"
    while zip_code:
        result_coords = []
        location_url = "https://order.papamurphys.com/Vendor/LocationResults?StreetAddress="+str(zip_code)
        r = session.get(location_url, headers=headers)      
        soup = BeautifulSoup(r.text, "lxml")
        data = soup.find(lambda tag: (tag.name == "script") and "$(document).ready(function()" in tag.text).text
        str_json =  data.split('OLO.Search.mapVendors = ')[1].split('OLO.Search.mapsCallback')[0].replace('}];','}]').replace("[];",'').strip().lstrip()
        if str_json:
            json_data = json.loads(str_json)
            current_results_len = len(json_data)
            for i in json_data:
                location_name = i['Name'].replace("\u0027","'")
                street_address = i['StreetAddress']
                city = i['City']
                state = i['State']
                latitude = i['Latitude']
                longitude = i['Longitude']
                page_url = i['Url']
                try:
                    r1 = session.get(page_url, headers=headers)
                except:
                    pass
                soup1 = BeautifulSoup(r1.text, "lxml")
                if soup1.find("dl",{"class":"available-hours"}) != [] and soup1.find("dl",{"class":"available-hours"}) != None:

                    hours = list(soup1.find("dl",{"class":"available-hours"}).stripped_strings)
                    hours_of_operation = ' '.join(hours)
                else:
                    hours_of_operation = "<MISSING>"
                if  soup1.find("span",{"class":"postal-code"}).text != None and soup1.find("span",{"class":"postal-code"}).text != []:
                    zipp = soup1.find("span",{"class":"postal-code"}).text
                else:
                    zipp = "<MISSING>"
                phone = soup1.find("span",{"class":"tel"}).text.strip().lstrip()
                result_coords.append((latitude, longitude))
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
