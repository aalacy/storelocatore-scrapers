from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import csv

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess =[]
    base_url = "https://www.untuckit.com"
    r = session.get("https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/5048/stores.js")
    data = r.json()["stores"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.untuckit.com")
        store.append(store_data['name'])
        location_request = session.get(store_data["url"])
        location_soup = BeautifulSoup(location_request.text,"lxml")
        address = list(location_soup.find("p",{"class":"store_info--copy"}).stripped_strings)
        st = address[0].replace("International Plaza Mall",'').replace("Copley Place",'').replace(",",' ').strip()
 
     
        if "london-covent-garden" in store_data["url"] or "london" in store_data["url"]:
            continue
        if "boca-raton" in store_data["url"]:
            st = store_data['address'].split(",")[0]
            city = store_data['address'].split(",")[1]
            state = store_data['address'].split(",")[-1].strip().split( )[0]
            us_zip = store_data['address'].split(",")[-1].strip().split( )[1]
        else:
            ca_zip_split = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',address[-1])
            if ca_zip_split:
                ca_zip = ca_zip_split[-1]
            else:
                ca_zip = ''
                us_zip_split = re.findall(r'[0-9]{5}',address[-1])
                us_zip = us_zip_split[0]
            state_split = re.findall(r'[A-Z]{2}',address[-1])
            if state_split:
                state = state_split[-1]
            city = address[-1].replace(state,"").replace(ca_zip,"").replace(us_zip,"").replace(",","")


        
        store.append(st.strip())
        store.append(city.strip())
        store.append(state.strip())
        store.append(ca_zip if ca_zip else us_zip)
        store.append("CA" if ca_zip else "US")
        store.append(store_data["id"])
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append("untuck it " + store_data["category"])
        store.append(store_data['latitude'])
        store.append(store_data['longitude'])
        hours_of_operation=''
        h = BeautifulSoup(store_data["description"],'lxml')
        hours_of_operation =  " ".join(list(h.stripped_strings)).replace("Open. Contactless ",'').replace("Pick Up & Same-Day Delivery also available.",'').replace("Open for Contactless Pickup & Same-Day Delivery also available.",'').split(".")[-1].strip()
        store.append(hours_of_operation if hours_of_operation != "" else "<MISSING>")
        store.append(store_data["url"])
        if str(store[2]+store[-1]) in addressess:
            continue
        addressess.append(str(store[2]+store[-1]))
        yield store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
