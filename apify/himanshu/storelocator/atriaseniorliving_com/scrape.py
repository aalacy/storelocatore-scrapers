import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # addresses = []
    country_code = "US"
    headers = {
            'accept':'*/*',
            'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }
    locator_domain = "https://www.atriaseniorliving.com/"

    ############################ US location ###############################

    r= session.get("https://www.atriaseniorliving.com/retirement-communities/search-state/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for state_link in soup.find("ul",{"id":"subpages"}).find_all("li"):
        # state_link_url = state_link.a["href"]
        # print("state === ",str(state_link.a.text))
        r1 = session.get(state_link.a["href"],headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        script = json.loads(soup1.find("script",text=re.compile("var CommunityList =")).text.split("var CommunityList = ")[1].split("};")[0]+"}")
        for x in script["communities"]:
            store_number = x["community_number"]
            location_name = x["name"]
            if "address_2" in x:
                street_address = x["address_1"]+" "+x["address_2"]
            else:
                street_address = x["address_1"]
            city = x["city"]
            state = x["state"]
            zipp = x["zip_code"]
            phone= x["phone"]
            latitude = x["latitude"]
            longitude = x["longitude"]
            services =  " , ".join(x["levels_of_service"])
            location_type = "<MISSING>"
            page_url = x["url"]
            hours_of_operation = "<MISSING>"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            # if str(str(store[1])+str(store[2])) not in addresses :
            #     addresses.append(str(store[1])+str(store[2]))

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            #print("data = " + str(store))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

    ############################ CA location ###############################

    r= session.get("https://atriaretirementcanada-atria.icims.com/",headers = headers)
    soup= BeautifulSoup(r.text,"lxml")
    for state_url in soup.find("div",class_="row provinces").find_all("a"):
        state_id = state_url["href"].split("=")[-1].strip()
        r1 = session.get("https://www.atriaretirement.ca/wp-content/themes/aslblanktheme/script-getstatelocations.php?state="+str(state_id),headers=headers).json()
        for loc in r1["communities"]:
            store_number  = loc["community_number"]
            location_name = loc["name"]
            if "address_2" in loc :
                street_address = loc["address_1"]+ " "+loc["address_2"] 
            else:
                street_address = loc["address_1"]
            city = loc["city"]
            state = loc["province"]
            zipp = loc["postal_code"]
            country_code = "CA"
            phone = loc["phone"]
            location_type = "<MISSING>"
            latitude =loc["latitude"]
            longitude = loc["longitude"]
            hours_of_operation = "<MISSING>"
            page_url = loc["url"]
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            # if str(str(store[1])+str(store[2])) not in addresses :
            #     addresses.append(str(store[1])+str(store[2]))

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
        
    
   
   


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
