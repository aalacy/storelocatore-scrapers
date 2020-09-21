import csv
import re
from  sgrequests import SgRequests
from bs4 import BeautifulSoup as BS
import json
session = SgRequests()

base_url = 'http://kuehne-nagel.com'



def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    for url in ['https://ca.kuehne-nagel.com/en_gb/other-links/our-locations-in-canada/','https://us.kuehne-nagel.com/en_gb/top-links/usa-locations']:
        soup = BS(session.get(url).text, "lxml")
        
        try:
            json_data = json.loads(json.loads(soup.find(lambda tag: (tag.name == "script") and "var inlineSettings =" in tag.text).text.split("var inlineSettings =")[1].split("if (typeof")[0].replace("};","}").strip())['locationList'])
        except:
            # print(url)
            pass
        for data in json_data:
            location_name = data['locationName']

            street_address = data['buildingNo'] +" "+ data['street'].replace("\r","").replace("\n","")

            if data['addressLine1']:
                street_address+= " " + data['addressLine1']
            if data['addressLine2']:
                street_address+= " " + data['addressLine2']
            city = data['city']
            state = data['stateRegion']
            zipp = data['postalCode']
            country_code = data['country']
            store_number = data['uid']
            phone = data['phoneNumber'].split("or")[0].split("x")[0]
            location_type = data['locationType']
            lat = data['latitude']
            lng = data['longitude']
            hours = data['openingHours'].replace("\r"," ").replace("\n"," ").replace("\t"," ")

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(url)
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print(store)
            yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
