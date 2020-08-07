# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.hobbylobby.com/"

    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        print("zip-code::::::::::"+str(search.current_zip))
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        location_url ="https://www.hobbylobby.com/store-finder?latitude="+str(lat)+"&longitude="+str(lng)+"&q="+str(search.current_zip)
        try:
            r = session.get(location_url, headers=headers)
        except:
            pass
        soup = BeautifulSoup(r.text.replace("'",''), "xml")
        str_json = soup.find("div",{"class":"map-canvas"})
        if str_json != [] and str_json != None:
            data = str(str_json).split('data-stores =')[1].split('</div>')[0].replace('&gt','').replace(";","")
            json_data = json.loads(data)
            current_results_len = len(json_data)
            for i in json_data:
                street_address = i['address1']
                city = i['city']
                state = i['stateProvinceCode']
                zipp = i['zipcode']
                phone = i['phone']
                latitude = round(float(i['latitude']),6)
                longitude = round(float(i['longitude']),6)
                store_number = i['linkUrl'].split('?')[0].split('/stores/search/')[1]
                lt = i['linkUrl'].split('=')[1]
                lg = i['linkUrl'].split('=')[2]
                href = "https://www.hobbylobby.com/"+str(i['linkUrl'].split('=')[0])+"="+str(lt[:5])+"&long="+str(lg[:6])
                try:
                    r1 = session.get(href, headers=headers)
                except:
                    pass
                soup1 = BeautifulSoup(r1.text, "lxml")
                hours = soup1.find("table",{"class":"store-openings weekday_openings"})
                if hours != [] and hours != None:
                    t = list(hours.stripped_strings)
                    hours_of_operation = ' '.join(t)
                else:
                    hours_of_operation = "<MISSING>"
            
                result_coords.append((latitude, longitude))
                store = []
                store.append(base_url)
                store.append("<MISSING>")
                store.append(street_address)
                store.append(city.replace("OFallon","O'Fallon"))
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append(store_number) 
                store.append(phone)
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append(href)
                if store[2] in addresses:
                    continue
                addresses.append(store[2]) 
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
