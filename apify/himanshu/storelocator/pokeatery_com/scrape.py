import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re

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
    base_url = 'http://www.pokeatery.com/'


    soup = bs(session.get(base_url).text, "lxml")
    
    for url in soup.find("ul",{"class":"sub-menu"}).find_all("a"):
        location_name = ''
        phone = ''
        page_url = url['href']

        location_soup = bs(session.get(page_url).text, "lxml")
        
        p_tag = location_soup.find_all("div",{"class":"container"})[1].find_all("p")

        if len(p_tag) == 2:

            hours = " ".join(list(p_tag[0].stripped_strings)).split("Hours:")[1].strip()
            addr = list(p_tag[1].stripped_strings)
            
            location_name = addr[0]
            street_address = addr[1]
            city = addr[2].split(",")[0]
            state = addr[2].split(",")[-1].split()[0]
            zipp = addr[2].split(",")[-1].split()[-1]
            phone = addr[3]

        elif len(p_tag) == 3:
            hours = " ".join(list(p_tag[0].stripped_strings)).split("Hours:")[1].strip()
            addr = list(p_tag[1].stripped_strings)

            street_address = addr[0].split(",")[0].split("\r\n")[0]
            city = addr[0].split(",")[0].split("\r\n")[1]
            state = addr[0].split(",")[1].split("\r\n")[0].split()[0]
            zipp = addr[0].split(",")[1].split("\r\n")[0].split()[1]
            phone = addr[0].split(",")[1].split("\r\n")[1]
        
        elif len(p_tag) == 4:
            hours = " ".join(list(p_tag[0].stripped_strings)).split("Hours:")[1].strip()

            if page_url == "http://www.pokeatery.com/san-mateo-california/":
                addr = list(p_tag[2].stripped_strings)

                street_address = addr[0]
                city = addr[1].split(",")[0]
                state = addr[1].split(",")[-1].split()[0]
                zipp = addr[1].split(",")[-1].split()[-1]
                phone = addr[2]
            else:
                addr =  list(p_tag[1].stripped_strings)
                street_address = addr[0].split(",")[0]
                city = addr[0].split(",")[1]
                state = addr[0].split(",")[-1].split()[0]
                zipp = addr[0].split(",")[-1].split()[1]
            
        
        elif len(p_tag) == 5:
            hours = " ".join(list(p_tag[1].stripped_strings)).split("Hours:")[1].strip()
            addr =  list(p_tag[2].stripped_strings)
            street_address = " ".join(addr[0].split(",")[0].split(" ")[:-1])
            city = addr[0].split(",")[0].split(" ")[-1]
            state = addr[0].split(",")[1].split()[0]
            zipp = addr[0].split(",")[1].split()[1]
            phone = " ".join(addr[0].split(",")[1].split()[2:])

        else:
            hours = " ".join(list(p_tag[1].stripped_strings))
            
            addr = list(p_tag[2].stripped_strings)
            street_address = addr[0]
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[-1].split()[0]
            zipp = addr[1].split(",")[-1].split()[-1]
            
            
            phone = p_tag[3].text

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        store.append(page_url)     
    
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        
        yield store
    
   

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
