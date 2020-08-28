import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip

session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["UK"])
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "UK"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    name=''
   
    while zip_code:
        result_coords = []
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        url = "https://www.prezzorestaurants.co.uk/find-and-book/search/?lat=0&lng=0&f=&s="+str(zip_code)+"&dist=Dist500"
        headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Host': 'www.prezzorestaurants.co.uk',
        'Referer': 'https://www.prezzorestaurants.co.uk/find-and-book/search/?lat=0&lng=0&f=&s='+str(zip_code)+'&dist=Dist500',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',

        }
        response = session.get(url, headers=headers)
        soup = bs(response.text,'lxml')
        current_results_len = len(soup.find_all("a",text=re.compile("Restaurant info")))
        for link in  soup.find_all("a",text=re.compile("Restaurant info")):
            page_url = "https://www.prezzorestaurants.co.uk"+link['href']
            # print(page_url)
            
            responsees = session.get(page_url, headers=headers)
            soup1 = bs(responsees.text,'lxml')
            addr = list(soup1.find("div",{"class":"restaurant-information__address"}).stripped_strings)
            street_address = " ".join(addr[:-2]).replace("Address","").strip()
            city = addr[-2].split(",")[-1].strip()
            zipp = addr[-1]
            phone = soup1.find("span",{'itemprop':"telephone"}).text.strip()
    
            try:
                hours_of_operation = " ".join(list(soup1.find("div",{'class':"restaurant-information__opening-times"}).stripped_strings)).replace("Temporarily Closed","<MISSING>")
            except:
                pass
           
            try:
                phone =soup1.find("span",{'itemprop':"telephone"}).text.strip()
            except:
                pass
            try:
                name = soup1.find("h1",{'itemprop':"name"}).text.strip()
            except:
                pass
            try:
                if "@" in soup1.find("a",text=re.compile("Get Directions"))['href']:
                    latitude = soup1.find("a",text=re.compile("Get Directions"))['href'].split("@")[-1].split(",")[0]
                else:
                    latitude = soup1.find("a",text=re.compile("Get Directions"))['href'].split("ll=")[1].split(",")[0]
            except:
                pass
            try:
                if "@" in soup1.find("a",text=re.compile("Get Directions"))['href']:
                    longitude = soup1.find("a",text=re.compile("Get Directions"))['href'].split("@")[-1].split(",")[1].split("&")[0]
                else:
                    longitude = soup1.find("a",text=re.compile("Get Directions"))['href'].split("ll=")[1].split(",")[1].split("&")[0]

            except:
                pass



            store_number=''
            result_coords.append((latitude,longitude))
            store = ["https://www.prezzorestaurants.co.uk/", name, street_address, city, state, zipp, "UK",
                    store_number, phone, "<MISSING>", str(latitude), str(longitude), hours_of_operation.replace("Opening times",'').strip(),page_url]
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2]  in addressess:
                continue
            addressess.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in  store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
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
