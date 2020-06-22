import csv
import re
import pdb
from lxml import etree
from bs4 import BeautifulSoup as BS
import json
from sgrequests import SgRequests
session = SgRequests()

base_url = 'https://arbys.com'



def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    con_soup = BS(session.get("https://locations.arbys.com/browse/").text, "lxml")

    for st_url in con_soup.find_all("a",{"data-ga":re.compile("Maplist, Region -")}):
        
        st_soup = BS(session.get(st_url['href']).text, "lxml")

        for ct_url in st_soup.find_all("a",{"data-ga":re.compile("Maplist, City")}):
            ct_soup = BS(session.get(ct_url['href']).text, "lxml")
            
            for url in ct_soup.find_all("a",{"class":"location-name ga-link"}):
                page_url = url['href']
                location_soup = BS(session.get(page_url).text,"lxml")

                json_data = json.loads(location_soup.find(lambda tag: (tag.name == "script") and '"addressLocality"' in tag.text).text)[0]
                location_name=location_soup.find("span",{"class":"location-name"}).text
                # location_name = json_data['name']
                street_address = json_data['address']['streetAddress']
                city = json_data['address']['addressLocality']
                state = json_data['address']['addressRegion']
                zipp = json_data['address']['postalCode']
                store_number = json_data['name'].split("Arby's")[-1].strip()
                phone = json_data['address']['telephone']
                location_type = json_data['@type']
                lat = json_data['geo']['latitude']
                lng = json_data['geo']['longitude']
                try:
                    hours = " ".join(list(location_soup.find("div",{"class":"hours"}).stripped_strings))
                except:
                    hours = "<MISSING>"
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US" if zipp.replace("-","").isdigit() else "CA")
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)
                yield store
    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
