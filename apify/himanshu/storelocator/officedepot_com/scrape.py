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

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 200
    MAX_DISTANCE = 250
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.officedepot.com/"

    while zip_code:
        result_coords = []

        # print("zip_code === "+zip_code)

        r = session.get('https://storelocator.officedepot.com/ajax?&xml_request=<request><appkey>AC2AD3C2-C08F-11E1-8600-DCAD4D48D7F4</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>500</limit><geolocs><geoloc><addressline>'+str(zip_code)+'</addressline></geoloc></geolocs><searchradius>'+str(MAX_DISTANCE)+'</searchradius>', headers=headers)
        
    
        soup = BeautifulSoup(r.text, "lxml")

        current_results_len = len(soup.find_all("poi"))

        for i in soup.find_all("poi"):
            if i.find("address2").text !='':
                location_name = i.find("address2").text
            else:
                location_name = "<MISSING>"
            
            street_address = i.find("address1").text
            city = i.find("city").text
            state = i.find("state").text
            zipp = i.find("postalcode").text
            country_code = i.find("country").text
            phone = i.find("phone").text
            store_number = i.find("clientkey").text
            location_type = i.find("icon").text
            latitude = i.find("latitude").text
            longitude = i.find("longitude").text
            hours_of_operation = "mon:" +" "+ str(i.find("mon").text)+" " + "tues:" +" "+ str(i.find("tues").text) +" "+ "wed:"+" " + str(i.find("wed").text)+" " + "thur:" +" "+ str(i.find("thur").text)+" " + "fri:" +" "+ str(i.find("fri").text)+" " + "sat:" +" "+ str(i.find("sat").text)+" " + "sun:"+" " + str(i.find("sun").text)
            page_url = "https://www.officedepot.com/storelocator/"+str(state.lower())+"/"+str(city.replace(' ','-').lower())+"/office-depot-"+str(store_number)+"/"
            
            result_coords.append((latitude, longitude))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number) 
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
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
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
