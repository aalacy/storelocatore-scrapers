import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    base_url = "https://www.subaru.com/"
    json_data = session.get("https://www.subaru.com/services/dealers/distances/by/zipcode?zipcode=66952&count=700&type=Active").json()

    for data in json_data:
        location_name = data['dealer']['name']
        street_address = (data['dealer']['address']['street']+ str(data['dealer']['address']['street2'])).strip()
        city = data['dealer']['address']['city']
        state = data['dealer']['address']['state']
        zipp = data['dealer']['address']['zipcode']
        store_number = data['dealer']['id']
        phone = data['dealer']['phoneNumber']
        lat = data['dealer']['location']['latitude']
        lng = data['dealer']['location']['longitude']
        page_url = data['dealer']['siteUrl']
        
        url = session.get(page_url).url + "dealership/directions.htm"
        soup = bs(session.get(url).text, "lxml")
        try:
            hours = " ".join(list(soup.find("div",{"data-widget-id":"hours1"}).stripped_strings)).replace("Hours","").replace("SALES HOURS","").strip()
        except:
            hours = "<MISSING>"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address.replace('None',''))
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
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        
        yield store
       
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
