
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    addresses = []
    base_url = "https://www.seat.co.uk"
    # print("remaining zipcodes: " + str(len(search.zipcodes)))
    soup = bs(session.get("https://dealersearch.seat.com/xml?app=seat-gbr&max_dist=0&city=W12%207GF&_=1591338622355").content, "lxml")
    result_coords = []
    for data in soup.find_all("partner"):
        street_address1=''
        location_name = data.find_all("name")[1].text
        # print(location_name)
        
        street_address = data.find("street").text
        city = data.find("city").text
        state =data.find("region_text").text
        zipp = data.find("zip_code").text
        phone = data.find("phone1").text
        latitude = data.find("latitude").text
        longitude = data.find("longitude").text
        page_url = "https://"+data.find("url").text.lower().replace("www.",'')
        store_number = "<MISSING>"
        hours="<MISSING>"
        store = []
        try:
            soup1 = bs(session.get(page_url.lower().replace("www.",'')).content, "lxml")
            hours = " ".join(list(soup1.find(lambda tag: (tag.name == "p" or tag.name == "h2") and "Opening Hours" == tag.text.strip()).next_element.next_element.next_element.next_element.stripped_strings))
        except:
            hours="<MISSING>"
        # soup1 = list(bs(session.get("https://"+page_url).content, "lxml").find("div",{"class":"feature-description richtext"}).stripped_strings)
        # print(soup1)
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("UK")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url if page_url else "<MISSING>")     
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        # print(store)
        yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
