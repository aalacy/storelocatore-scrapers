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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    base_url = "http://www.costcutters.com"
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["US","CA"])
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    coord = search.next_coord()
    country_code = "US"
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    }
    while coord:
        result_coords = []
        x = coord[0]
        y = coord[1]
        #print(coord)
        # url="https://info3.regiscorp.com/salonservices/siteid/100/salons/searchGeo/map/33.5973469/-112.10725279999997/0.8/0.8/true"
        try:
            r = requests.get("https://info3.regiscorp.com/salonservices/siteid/100/salons/searchGeo/map/"+str(x)+"/"+str(y)+"/0.8/0.8/true", headers=headers).json()
        except:
            pass       
        # print()
        for i in r['stores']:
            location_name = i['title']
            street_address = i['subtitle'].split(',')[0]
            try:
                zip1= " ".join(i['subtitle'].split(",")[-1].split( )[1:])
            except:
                zip1 = ""

            # print("----------------------  ",i['subtitle'])
            city = i['subtitle'].split(',')[1].strip()
            # print("~~~~~~~~~~ ",city)
            # state = i['subtitle'].split(',')[-1].split(" ")[1]
            # zipp = i['subtitle'].split(',')[-1].split(" ")[2]

            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zip1))
            # print(ca_zip_list)
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zip1))
            state_list = re.findall(r' ([A-Z]{2})', str(i['subtitle']))

            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
            # print(zipp)
            if state_list:
                state = state_list[-1]

            # print("~~~~~~~~~~~",state)

            # if len(zipp)==5:
            #     country_code="US"
            # else:
            #     country_code="CA"
            store_number = i['storeID']
            #print(store_number)
            latitude = i['latitude']
            longitude = i['longitude']
            phone = i['phonenumber']
            hours = ''
            for time in  i['store_hours']:
                hours+= time['days']+" "+time['hours']['open']+"-"+time['hours']['close']
            hours = hours
            page_url = "https://www.signaturestyle.com/locations/"+str(state.lower())+"/"+str(city.lower())+"/cost-cutters-"+str(location_name.lower().replace(" ","-"))+"-haircuts-"+str(store_number)+".html"
            

            result_coords.append((latitude,longitude))
            store=[]
            if "(0) 0-0" in phone:
                phone1 = "<MISSING>"
            else:
                phone1 = phone 
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address.strip() if street_address else "<MISSING>")
            store.append(city.strip() if city else "<MISSING>")
            store.append(state.strip() if state else "<MISSING>")
            store.append(zipp.strip() if zipp else "<MISSING>")
            store.append(country_code)
            store.append(store_number if store_number else "<MISSING>")
            store.append(str(phone1).strip() if phone1 else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude )
            store.append(longitude)
            store.append(hours.strip() if hours else "<MISSING>")
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
            # print("data===="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")


        if len(r['stores']) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(r['stores']) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
