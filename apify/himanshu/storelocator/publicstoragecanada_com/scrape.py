import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import time

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

    addressess = []
    base_url = "https://publicstoragecanada.com"
    
    
    
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "x-requested-with":"XMLHttpRequest",
        "content-type" :"application/x-www-form-urlencoded; charset=UTF-8",
    }
   
    
    state_soup = bs(session.get(base_url, headers=headers).content, "lxml")
    
        
    for city_link in state_soup.find_all("li",{"class":re.compile("menu-item menu-item-type-taxonomy menu-item-object-location_city menu-item")}):

       city_soup = bs(session.get(city_link.a['href'], headers=headers).content, "lxml")

       for link in city_soup.find_all("a",{"class":"secondaryText"}):

            if "http" not in link['href']:
               continue

            page_url = link['href']

            location_soup = bs(session.get(page_url , headers=headers).content, "lxml")

            location_name = location_soup.find("h1").text.strip()

            addr = location_soup.find("div",{"class":"singleLocationAddress"}).find_all("p")

            street_address = addr[0].text.strip()
            city = addr[1].text.split(",")[0].strip()
            state = addr[1].text.split(",")[1].strip()
            zipp = addr[2].text.strip()
            
            if "201 Romina Dr" in street_address:
                state = "ON"
            store_number = re.findall(r'[0-9]+',location_soup.find(lambda tag: (tag.name == "script") and "locationid" in tag.text).text)
            
            if store_number:
                store_number = store_number[-1]
            else:
                store_number = "<MISSING>"
 
            phone = location_soup.find(lambda tag: (tag.name == "script") and "locphone" in tag.text).text.split('"')[1].strip()
            
            lat = location_soup.find(lambda tag: (tag.name == "script") and "var lat =" in tag.text).text.split('"')[1].strip()
            lng = location_soup.find(lambda tag: (tag.name == "script") and "var lng =" in tag.text).text.split('"')[1].strip()
            
            hours = " ".join(list(location_soup.find("div",{"class":"singleLocationOfficeHours marginB30"}).stripped_strings)).split("hours.")[1].strip()
        
           

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("CA")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url) 
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] + store[-1] in addressess:
                continue
            addressess.append(store[2] + store[-1])
            yield store
                  
      


def scrape():
    data  = fetch_data()
    write_output(data)

scrape()
