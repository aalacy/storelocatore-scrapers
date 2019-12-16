import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.ruthschris.com/restaurant-locations/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    a = soup.find_all("script")
   

    for i in a :
        if "utils.restaurants" in i.text:
            json_data = json.loads(i.text.split("utils.restaurants =")[1].split("locationsMap.init()")[0].replace("];",']'))
            for k in json_data:
                location_name = k['Name']
                street_address = k['Address1']
                city = k['City']
                state = k['State']
                zipp1 = k['Zip']
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp1))
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp1))
                if us_zip_list:
                    zipp = us_zip_list[-1]
                    country_code = "US"
                phone =k['Phone']
                latitude  = k['Latitude']
                longitude = k['Longitude']
                page_url = k['Url']
                r1 = requests.get(page_url)
                soup1= BeautifulSoup(r1.text,"lxml")
                b = (soup1.find("div",{"class":"container hours"}))
                if b != None and b != [] :
                    m = list(b.stripped_strings)
                    hours_of_operation =  ''.join(m)
                else:
                    hours_of_operation = "<MISSING>"
                store = []
                store.append("https://www.ruthschris.com")
                store.append(location_name if location_name else "<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code)
                store.append("<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation)
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store
                
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
