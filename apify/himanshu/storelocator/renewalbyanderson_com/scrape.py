import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" ,"page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    address = []
    base_url= "https://www.renewalbyandersen.com"
    location_url = "https://www.renewalbyandersen.com/about/renewal-by-andersen-showrooms"
    r= session.get(location_url, headers=headers)
    soup=BeautifulSoup(r.text, "lxml")
    locations = soup.find_all("div",{"class":"row component column-splitter"})[6:8]
    for location in locations:
        for link in location.find_all("a"):
            if "item=web%3a%7b1C875120-4431-4506-BD46-9B579A66DBD1%7d%40en" not in link['href']:
                href = "https://www.renewalbyandersen.com/"+link['href']
                r1 = session.get(href, headers=headers)
                soup1 = BeautifulSoup(r1.text, "lxml")
                coords = soup1.find("map-config",{"style":"display: none;"})
                latitude = str(coords).split('"Latitude":')[3].split(',')[0]
                longitude = str(coords).split('"Latitude":')[3].split(',')[1].split('"Longitude":')[1].split(',')[0]
                data = soup1.find("div",{"class":"component address-hours o-flex--column columns"})
                if data != None and data != []:
                    info = list(data.stripped_strings)
                    location_name = info[0]
                    street_address = info[2]
                    city = info[3].split(',')[0]
                    state = info[3].split(',')[1].split(' ')[1]
                    zipp = ''.join(info[3].split(',')[1].split(' ')[2:]).replace('L5L5Y7','L5L 5Y7')
                    if location_name == "Delta" or location_name == "Toronto":
                        country_code = "CA"
                    else:    
                        country_code = "US"
                    phone = info[5]
                    hours_of_operation = " ".join(info[7:])  
                
                store = []
                store.append(base_url)
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code)
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(href)
                store = [x.strip() if x else "<MISSING>" for x in store]
                if store[2] in address:     
                    continue
                address.append(store[2])
                yield store
            

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
