import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('boulevardtire_com')


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = locator_domain = "https://www.boulevardtire.com/"
    addresses=[]
    country_code = "US"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    r= session.get("https://www.boulevardtire.com/Locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for loc in soup.find_all("div",class_="loclisting"):
        subtitle = loc.find("p",class_="subtitle").text.split("-")[-1].replace("Location Details","").strip()
        page_url = loc.find("a",class_="DetailLink")["href"]
        address = list(loc.find("div",class_="locationInfo").stripped_strings)
        location_name = address[0]
        manager = address[1]
        street_address = address[2]
        city = address[-1].split(",")[0]
        state = address[-1].split(",")[-1].split()[0]
        zipp = address[-1].split(",")[-1].split()[-1]
        hours_of_operation = " ".join(list(loc.find("div",class_="locationhours").stripped_strings)).replace("Hours","").strip()
        phone = loc.find("div",class_="locphone").a.text.strip()
        store_number = page_url.split("Mode/")[1].split("/")[0].strip()
        latitude = loc.find("span",class_="hideDistance distance")["lat"].strip()
        longitude = loc.find("span",class_="hideDistance distance")["lon"].strip()
        if "0" == latitude and "0" == longitude:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        if "Retread" in location_name:
            location_type= "Retread"
        else:
            retail_loc_url = "https://www.boulevardtire.com/Retail-Locations/"+city.replace(" ","-")+"-"+state
            r1 = session.get(retail_loc_url,headers=headers)
            soup1 = BeautifulSoup(r1.text,"lxml")
            phone_tag= soup1.find("div",class_="pc-body").text.strip()
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
            if phone_list:
                if phone == phone_list[0]:
                    location_type = "Retail"
                    # logger.info(phone)
                    # logger.info(street_address)
                    # logger.info(retail_loc_url)
            else:
                location_type = "Commercial"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                            store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        
        if (str(store[1])+str(store[2])+str(store[-5])) not in addresses:
            addresses.append(str(store[1])+str(store[2])+str(store[-5]))

            
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
                    
            
        




def scrape():
    data = fetch_data()
    write_output(data)

scrape()
