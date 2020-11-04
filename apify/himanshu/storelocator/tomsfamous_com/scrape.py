import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json


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
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://tomsfamous.com"
    
    soup = bs(session.get("https://tomsfamous.com/locations/",headers=headers).text,"lxml")
    
    for name in soup.find_all("span",text=re.compile("TOM'S ")):
        location_name = name.text

        page_url = "https://tomsfamous.com/" + str(name.text.lower().replace("'","").replace(" ","-"))
        
        
        location_soup = bs(session.get(page_url, headers=headers).text, "lxml")
        if location_soup.find("h1",{"class":"page-title"}):
            continue
      
        info = list(location_soup.find(lambda tag:(tag.name == "div") and "TOM'S " in tag.text).find("div",{"class":"elementor-inner"}).stripped_strings)
        
        street_address = info [1]
        city = info[2].split(",")[0]
        state = info[2].split(",")[1].split()[0]
        zipp = info[2].split(",")[1].split()[1]
        phone = info[3]
        hours = info[-2].replace("CLOSED UNTIL FURTHER NOTICE","<MISSING>")
        store_number = location_name.split()[-1]

        geo_soup = bs(session.get(location_soup.find("iframe")["src"],headers=headers).text,"lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in script.text:
                lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)     
    
        store = [str(x).replace("–","-").strip() if x else "<MISSING>" for x in store]

        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
