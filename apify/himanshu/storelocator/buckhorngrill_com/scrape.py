import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('buckhorngrill_com')




session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
 
def fetch_data():
    addressess = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://buckhorngrill.com"
   
    r = session.get("https://buckhorngrill.com/locations/",headers=headers)
    soup=BeautifulSoup(r.text,'lxml')

    data_link = str(soup).split('var link = "')
    for i in data_link[1:]:
        link = i.split("var location_type")[0].replace('";\n','').strip()
        
        link_r = session.get(link,headers=headers)
        link_soup = BeautifulSoup(link_r.text,'lxml')

        location_name = link_soup.find("h2",{"class":"location-title"}).text
        # logger.info(name)
        addr = link_soup.find("p",{"class":"location-address"}).text.split(",")
        # logger.info(addr)
        # logger.info(len(addr))
        if len(addr) == 3:
            street_address = addr[0]
            city = addr[1].strip()
            temp_state_zip = addr[2].strip().split(" ")
            if len(temp_state_zip)==2:
                state = temp_state_zip[0].upper()
                zipp = temp_state_zip[1]
            else:
                state = temp_state_zip[0]
                zipp = "<MISSING>"
        elif len(addr) == 2:
           
            if location_name == "Walnut Creek":
                city = "Walnut Creek"
                street_address = addr[0].replace(city,"").strip()
                temp_state_zip = addr[1].strip().split(" ")
                state = temp_state_zip[0]
                zipp = temp_state_zip[1]
            if location_name == "SF Metreon: Temporarily Closed":
                city = "San Francisco"
                street_address = addr[0].replace(city,"").strip()
                temp_state_zip = addr[1].strip().split(" ")
                state = temp_state_zip[0]
                zipp = temp_state_zip[1]
            if location_name == "Roseville: Temporarily Closed":
                city = "Roseville"
                street_address = addr[0].replace(city,"").strip()
                temp_state_zip = addr[1].strip().split(" ")
                state = temp_state_zip[0]
                zipp = temp_state_zip[1]
            if location_name == "Pleasanton: Temporarily Closed":
                city = "Pleasanton"
                street_address = addr[0].replace(city,"").strip()
                temp_state_zip = addr[1].strip().split(" ")
                state = temp_state_zip[0]
                zipp = temp_state_zip[1]
            if location_name == "Modesto":
                city = location_name
                state = "California"
                street_address = " ".join(addr).replace(city,"").replace(state,"").strip()
                zipp = "<MISSING>"
        else:
            city = location_name.split(" ")[0]
            if location_name == "Vacaville":
                street_address = addr[0]
                city = "Vacaville"
            temp_addr = addr[0].split(" ")
            street_address = " ".join(temp_addr[:-1]).replace(city,"").strip()
            state = temp_addr[-1]
            zipp = "<MISSING>"
        
        country_code = "US"
        store_number = "<MISSING>"
        phone = link_soup.find("h5",{"class":"phone-number"}).text
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = link_soup.find_all("div",{"class":"hours"})
        hour = []
        for h in hoo:
            hour.append(" ".join(list(h.stripped_strings)).replace("Current Hours:","").replace("Hours:","").strip())
        
        hours_of_operation = ", ".join(hour)

        page_url = link


        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address.replace('1650 East Monte Vista','1650 East Monte Vista Ave'))
        store.append(city)
        store.append(state.replace('Ave','<MISSING>'))
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [x.replace("–","-") if type(x) == str else x for x in store]
    
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store



def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)
scrape()
