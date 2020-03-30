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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://foodkingcostplus.com"
    r = session.get(base_url + "/contact-us/")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []

    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if "gmpAllMapsInfo" in script.text:
            location_list = json.loads(script.text.split("gmpAllMapsInfo = ")[1].split("];")[0] + "]")[0]["markers"]
            for i in range(len(location_list)):
                store_data = location_list[i]
                store = []
                store.append("https://foodkingcostplus.com")
                store.append(store_data["icon_data"]["title"])
                cleanr = re.compile('<.*?>')
                try:
                    store_address_details = []
                    store_address_details.append(re.sub(cleanr, '', store_data["address"].split(",")[0]))
                    store_address_details.append(re.sub(cleanr, '', store_data["address"].split(",")[1]))
                    store_address_details.append(re.sub(cleanr, '', store_data["address"].split(",")[2].split(" ")[1]))
                    store_address_details.append(re.sub(cleanr, '', store_data["address"].split(",")[2].split(" ")[2]))
                    store.extend(store_address_details)
                except:
                    store_address_details = []
                    store_address_details.append(re.sub(cleanr, '', store_data["description"].split("<p>")[1].split("</p>")[0].split(",")[0]))
                    store_address_details.append(re.sub(cleanr, '', store_data["description"].split("<p>")[1].split("</p>")[0].split(",")[1]))
                    store_address_details.append(re.sub(cleanr, '', store_data["description"].split("<p>")[1].split("</p>")[0].split(",")[2].split(" ")[1]))
                    store_address_details.append(re.sub(cleanr, '', store_data["description"].split("<p>")[1].split("</p>")[0].split(",")[2].split(" ")[2]))
                    store.extend(store_address_details)
                store.append("US")
                store.append(store_data["id"])
                store.append(re.sub(cleanr, '', store_data["description"].split("Phone:")[1].split("</p>")[0].strip().split("</div>")[0]))
                store.append("food king costplus")
                store.append(store_data["position"]["coord_y"])
                store.append(store_data["position"]["coord_x"])
                store.append(store_data["description"].split("Store Hours:")[1].split("</p>")[0].strip().split("</div>")[0].split("<br")[0])
                if len(store[-1].split(">")) >= 2 and "</span>" in store[-1]:
                    store[-1] = store[-1].split(">")[1].split("</span>")[0]
                store[-1] = re.sub(cleanr, '', store[-1])
                store[-1] = store[-1].split("</span")[0]
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
