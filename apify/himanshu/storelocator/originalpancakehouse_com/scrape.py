import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time 

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    address = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url = "http://originalpancakehouse.com/"
    location_url = "http://originalpancakehouse.com/locations.html"
    r = session.get(location_url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for i in soup.find("ul",{"id":"state_list"}).find_all("a"):
        link = (i['href'])
        page_url = "http://originalpancakehouse.com/"+str(link)
        r1 = session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml") 
        for y in soup1.find("div",{"class":"locations"}).find_all("div",{"class":"location"}):
            data = list(y.stripped_strings)
            if "Show\n" in data[-1]:
                del data[-1]
            if "Map" in data[-1]:
                del data[-1]
            if "Contact" in data[3]:
                del data[3]
            if "Redmond Town Center" in data[1]:
                del data[1]
            if "Suite F101" in data[2]:
                del data[2]
            if "15 the Promenade" in data[2]:
                del data[2]
            if "1700 West Parmer" in data[2]:
                del data[2]
            if "Forest Drive" in data[2]:
                del data[2]
            if "Building A, Suite 120" in data[2]:
                del data[2]
            location_name = re.sub(r'\s+'," ",data[0])
            street_address = re.sub(r'\s+'," ",data[1].replace("\n","").replace("\t","")).replace("41377 Margarita Road","41377 Margarita Road Suite F101").replace("City Place","City Place 15 the Promenade").replace("Scofield Farms Market","Scofield Farms Market 1700 West Parmer Lane").replace("Trenholm Plaza","Trenholm Plaza 4840 Forest Drive").replace("5530 Windward Parkway","5530 Windward Parkway Building A, Suite 120")
            raw_city = re.sub(r'\s+'," ",data[2]).replace("Grosse Pointe Woods, Michigan, 48236","Grosse Pointe Woods, Michigan 48236")
            city = raw_city.split(",")[0]
            if len(raw_city.split(",")[1].split(" ")) == 3:
                state = raw_city.split(",")[1].split(" ")[1]
                zipp = raw_city.split(",")[1].split(" ")[2]
            else:
                state = " ".join(raw_city.split(",")[1].split(" ")[:-1]).strip()
                zipp = raw_city.split(",")[1].split(" ")[-1]
            del data[0]
            del data[0]
            del data[0]
            if "Contact" in data[0]:
                del data[0]
            if "Hours" in data:
                phone = data[0].replace("Phone:","").strip()
                if "Phone" in data[0]:
                    del data[0]
                if "Email:" in data[0]:
                    del data[0]
                if "@" in data[0]:
                    del data[0]
                if "Website:" in data[0]:
                    del data[0]
                if "www" in data[0]:
                    del data[0]
                if "Fax" in data[0]:
                    del data[0]
                if "Email" in data[0]:
                    del data[0]
                if "@" in data[0]:
                    del data[0]
                if "Website:" in data[0]:
                    del data[0]
                if "www" in data[0]:
                    del data[0]
                hours = re.sub(r'\s+'," ",str(" ".join(data[1:])))
            else:
                hours = "<MISSING>"
                phone = data[0].replace("Phone:","").strip()


                
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("pancakehouse")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append(hours)
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store 

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
