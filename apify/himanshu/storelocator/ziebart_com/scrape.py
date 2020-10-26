import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    addresses = []
    
    base_url = locator_domain="https://www.ziebartworld.com/"
    

    data = {"Longitude": "-71.1987762451",
    "Latitude": "46.8758392334",
    "callBack": "init_map",
    "telEnMobile": "1"}    
    r_json = session.post("https://www.uniglassplus.com/inc/ajax/rechSuccursale.cfm", data=data).json()
    for data in r_json['ARRSUCCURSALE']:
        location_name = data['SUCCURSALENOM']
        street_address = data['ADRESSE']
        city = data['VILLE']
        state = data['PROVINCE']
        zipp = data['CP']
        country_code = "CA"
        store_number = data['SUCCURSALEID']
        phone = data['TEL']
        location_type = data['SUCCURSALETYPE']
        latitude = data['POSLATITUDE']
        longitude = data['POSLONGITUDE']
        page_url = data['LIENDETAIL']
        
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            hours_of_operation = " ".join(list(soup1.find("div",{"id":"horaireSucc"}).stripped_strings))
        except:
            hours_of_operation = "<MISSING>"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses:
            addresses.append(str(store[1]) + str(store[2]))

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
    
    #----- us locations ------#
    
    # print("start")
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    # coord = search.next_coord()
    current_results_len = 0 
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = "<MISSING>"
        phone = ""
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        raw_address = ""
        page_url = ""
        hours_of_operation = ""

        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        page =1
        while True:
            r= session.get("https://www.ziebart.com/find-my-ziebart?zipcode="+str(zip_code)+"&distance=100&page="+str(page),headers= headers)
            soup = BeautifulSoup(r.text,"lxml")
            # print(page)
            ul = soup.find("ul",class_="sfStoreList")
            if ul:
                for li in ul.find_all("li",class_="store-detail"):
                    current_results_len = len(li)
                    page_url = "https://www.ziebart.com"+li.find("div",class_="location-info-div").find("a")["href"]
                    location_name = li.find("div",class_="location-info-div").h4.text.split(",")[0].strip()
                    latitude = li.find("div",class_="topmapimg").find("iframe")["src"].split("sspn=")[1].split(",")[0].strip()
                    longitude = li.find("div",class_="topmapimg").find("iframe")["src"].split("sspn=")[1].split(",")[1].split("&")[0].strip()
                    phone = li.find("span",class_="phone-digits").text.strip()
                    r1 = session.get(page_url,headers = headers)
                    soup1 = BeautifulSoup(r1.text,"lxml")
                    address = list(soup1.find("div",class_="store-detail-text").stripped_strings)
                    street_address = " ".join(address[:-1]).strip()
                    city = address[-1].split(",")[0].strip()
                    state = address[-1].split(",")[-1].split()[0].strip()
                    zipp = address[-1].split(",")[-1].split()[-1].strip()
                    hours_of_operation = " ".join(list(soup1.find_all("div",class_="store-detail-left")[-1].stripped_strings)).replace("Hours:","").replace("Credit Cards Accepted","").strip()
                    result_coords.append((latitude,longitude))
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]


                    if (str(store[2])+str(store[-1])) in addresses:
                        continue
                    addresses.append(str(store[2])+str(store[-1]))

                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    
                    yield store
                    
                page += 1
            else:
                break
            
        
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
