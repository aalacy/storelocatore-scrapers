import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    adressess = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    base_url = "https://www.lapetite.com"
    # data = {
    #     'location': '11756',
    #     'range': '1000'

    # }
    while zip_code:
        result_coords =[]
        #print("zip_code === "+zip_code)
       # print("remaining zipcodes: " + str(len(search.zipcodes)))

        r = session.get("https://www.lapetite.com/child-care-centers/find-a-school/search-results/?location="+ str(zip_code) +"&range=100",headers=headers)
        soup = BeautifulSoup(r.text,"lxml")

        for location in soup.find_all("div",{'class':"locationCard"}):
            name = location.find("a",{'class':"schoolNameLink"}).text
            address = location.find("span",{'class':"street"}).text
            address2 = location.find("span",{'class':"cityState"}).text
            store_id = location["data-school-id"]
            if location.find("span",{'class':"tel"}) != None:
                phone = location.find("span",{'class':"tel"}).text
            elif location.find("p",{'class':"phone"}) != None:
                phone = list(location.find("p",{'class':"phone"}).stripped_strings)[-1]
            else:
                phone = "<MISSING>"
            hours = " ".join(list(location.find("p",{'class':"hours"}).stripped_strings))

            if name.split(" ")[0] == "Childtime":
                page_url = location.find("a",{'class':"schoolNameLink"})['href']
                location_type = "Childtime"
            elif name.split(" ")[0] == "Tutor":
                page_url = location.find("a",{'class':"schoolNameLink"})['href']
                location_type = "Tutor Time"
            elif name.split(" ")[0] == "Everbrook":
                page_url = location.find("a",{'class':"schoolNameLink"})['href']
                location_type = "Everbrook Academy"
            elif name.split(" ")[-1] == "Montessori":
                page_url = location.find("a",{'class':"schoolNameLink"})['href']
                location_type = "Montessori"
            elif name.split(" ")[1] == "Montessori":
                page_url = location.find("a",{'class':"schoolNameLink"})['href']
                location_type = "Montessori"
            elif "The Children's Courtyard" in name:
                page_url = location.find("a",{'class':"schoolNameLink"})['href']
                location_type = "The Children's Courtyard"


            else:
                page_url = "https://www.lapetite.com" + location.find("a",{'class':"schoolNameLink"})['href']
                location_type = "lapetite"

            store = []
            store.append("https://www.lapetite.com")
            store.append(name)
            store.append(address)
            store.append(address2.split(",")[0])
            store.append(address2.split(",")[1].split(" ")[1])
            store.append(address2.split(",")[1].split(" ")[-1])
            store.append("US")
            store.append(store_id)
            store.append(phone if phone != "" else "<MISSING>")
            store.append(location_type)
            store.append(location.find("span",{"class":"addr"})["data-latitude"])
            store.append(location.find("span",{"class":"addr"})["data-longitude"])
            store.append(hours)
            store.append(page_url)
            if store[2] in adressess:
                continue
            adressess.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
            
        if len(location) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(location) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        
        zip_code = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
