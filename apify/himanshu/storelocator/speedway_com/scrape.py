import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.speedway.com/"
    r = session.post("https://www.speedway.com/Locations/Search",headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("section",{"class":"c-location-card"})
    for i in data:
        phone = i.find("li",{"data-location-details":"phone"}).text
        street_address = i.find("a",{"class":"btn-get-directions"})['data-location-address'].split(',')[0] 
        city = i.find("li",{"data-location-details":"address"}).text.split(',')[0]
        state = i.find("li",{"data-location-details":"address"}).text.split(',')[1].split(' ')[1]
        zipp = i.find("li",{"data-location-details":"address"}).text.split(',')[1].split(' ')[2]
        store_number = i['data-costcenter']
        latitude = i['data-latitude']
        longitude = i['data-longitude']
        page_url = "https://www.speedway.com/locations/store/"+str(store_number)
        hours = soup.find_all("ul",{"class":"c-location-options__list"})[1]
        if "Open 24 Hours" in hours.find("li").text.strip().lstrip():
            hours_of_operation = hours.find("li").text.strip().lstrip()
        else:
            hours_of_operation = "<MISSING>"    
        
        store = []
        store.append(base_url)
        store.append("<MISSING>")
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number) 
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        
        yield store
def scrape():
    data = fetch_data()

    write_output(data)


scrape()




        
    

