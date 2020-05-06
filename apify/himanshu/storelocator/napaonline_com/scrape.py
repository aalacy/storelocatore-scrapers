import csv
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip
from sgrequests import SgRequests


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    addresses5=[]
    search = sgzip.ClosestNSearch()    
    search.initialize(country_codes=["US"])
    MAX_RESULTS = 300
    MAX_DISTANCE = 22
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        base_url = "https://www.napaonline.com"
        headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        'accept': 'text/html, */*; q=0.01'
        }
        #print("https://www.napaonline.com/en/store-finder?q="+str(zip_code)+"&sort=true")
        try:
            r = session.get("https://www.napaonline.com/en/store-finder?q="+str(zip_code)+"&sort=true", headers=headers)
        except:
            pass
        soup = BeautifulSoup(r.text, "lxml")
        latitude = []
        longitude = []
        if soup.find("div", {"id":"map_canvas"}) != None:
            json_data = json.loads(soup.find("div", {"id":"map_canvas"})['data-stores'])
            
            for i in range(len(json_data)):
                latitude.append(json_data['store'+str(i)]['latitude'])
                longitude.append((json_data['store'+str(i)]['longitude']))

        data_len = len(soup.find_all("div",{"class":"pure-g"}))
        for index,data in enumerate(soup.find_all("div",{"class":"pure-g"})):
            page_url = base_url + data.find("a",{"class":"storeWebsiteLink"})['href']
            location_name = re.sub(r'\s+'," ",data.find("a",{"class":"storeWebsiteLink"}).text)
            street_address = (data.find("div",{"class":"address-1"}).text + str(data.find("div",{"class":"address-2"}).text)).strip()
            addr = re.sub(r'\s+'," ",(data.find_all("div",{"class":"address-2"})[-1].text)).replace("Punta Gorda, FL, FL 33950","Punta Gorda, FL 33950")
            city = addr.split(",")[0]
            state = addr.split(",")[1].split(" ")[1]
            zipp = addr.split(",")[1].split(" ")[2].replace("00000","<MISSING>")
            if state == "32330":
                state = "<MISSING>"
                zipp = "32330"
            if state == "21960":
                state = "<MISSING>"
                zipp = "21960"
            if state == "96799":
                state = "<MISSING>"
                zipp = "96799"
            if state == "St.":
                state = "St. Croix"
                zipp = "00820"
            if state == "96929":
                state = "<MISSING>"
                zipp = "96929"
            store_number = page_url.split("/")[-1]
            phone = re.sub(r'\s+'," ",data.find("div",{"class":"phone"}).text)
            if phone == " 0 ":
                phone = "<MISSING>"
            location_type = "Auto Parts"
            hours = " ".join(list(data.find("div",{"class":"store-hours"}).stripped_strings)).replace('Shop this Store','').replace("no online reservations Reserve Online Not Available. Why? We' re sorry, this store does not participate in Reserve Online. Please choose another store.",'').strip()

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state.replace("00000","<MISSING>" if state else "<MISSING>"))
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append(store_number)
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append(latitude[index])
            store.append(longitude[index])
            store.append(hours)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # print("data ====="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            yield store
        
        try:
            r1 = session.get("https://www.napaonline.com/api/storelocator/nearby-stores?storeType=ACMEC&location="+str(zip_code)+"&sortBy=1&language=en", headers=headers).json()
        except:
            pass
        # soup1 = BeautifulSoup(r1.text, "lxml")
        current_results_len= data_len+len(r1['DetailResponse'])
        for data in r1['DetailResponse']:
            state=data['Basic']['address'].split(",")[-2]
            city = data['Basic']['address'].split(",")[-3]
            street_address=(" ".join(data['Basic']['address'].split(",")[:-3]))
            hour = ''
            for h in data['Basic']['StoreHours']['hours']:
                hour = hour + ' '+ h
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(data['Basic']['address']))
            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            store_number=data['Basic']['facilityId']
            store = []
            store.append("https://www.napaonline.com/")
            store.append(data['Basic']['facilityName'])
            store.append(street_address)
            store.append(city)
            store.append(state.replace("00000","<MISSING>" if state else "<MISSING>"))
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append(store_number)
            store.append(data['Basic']['facilityPhoneNumber'] if data['Basic']['facilityPhoneNumber'] else "<MISSING>")
            store.append("Auto Care")
            store.append(data['Basic']['StoreGeoLocation']['latitude'])
            store.append(data['Basic']['StoreGeoLocation']['longitude'])
            store.append(hour.replace("|",":"))
            store.append("https://www.napaonline.com/en/autocare/?facilityId="+str(store_number))
            if store[2] in addresses5:
                continue
            addresses5.append(store[2])
            # print("data ====="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
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

