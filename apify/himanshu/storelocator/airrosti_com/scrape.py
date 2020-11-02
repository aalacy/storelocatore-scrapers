
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('airrosti_com')


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
    addresses = []
    soup = bs(session.get("https://www.airrosti.com/locations/",headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}).text,'lxml')
    data = json.loads(soup.find(lambda tag: (tag.name == "script" ) and "air_locations" in  tag.text.strip()).text.split("var air_locations =")[1].split("}];")[0]+"}]")
    for data in data:
        street_address =data["addr1"]+' '+data['addr2']
        location_name = data["prac"]
        city = data['city']
        zipp = data['zip']
        state = data['st']
        longitude =data['lng']
        latitude =data['lat']
        page_url = "https://www.airrosti.com/"+state+"/"+data['locid']
        if "https://www.airrosti.com/TX/ALLEN" in  page_url:
            page_url="https://www.airrosti.com/location/Texas/ALLEN/"
        phone=''
        soup1 = bs(session.get(page_url,headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}).text,'lxml')
        try:
            phone =soup1.find("div",{"class":"locPhone"}).text.strip()
        except:
            phone=''
        hours=''
        try:
            hours=(" ".join(list(soup1.find("div",{"class":"nomobile wpb_column vc_column_container vc_col-sm-6"}).stripped_strings)))
        except:
            hours=''
        store_number = data['id']
        store = []
        store.append("https://www.airrosti.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url if page_url else "<MISSING>")     
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip().replace("0.000000","<MISSING>").replace("HOURS ",'') if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ",store)
        yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
