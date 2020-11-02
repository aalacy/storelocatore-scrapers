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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://limefreshmexicangrill.com"
    r = session.get("https://limefreshmexicangrill.com/wp-content/themes/lime/map.php",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_request = session.get("https://limefreshmexicangrill.com/lime-locations/",headers=headers)
    location_soup = BeautifulSoup(location_request.text,"lxml")
    location_data = {}
    for location in location_soup.find("aside").find_all("li"):
        name = location.find_all("a")[1].text
        if "COMING SOON" in location.find("a").text:
            location_data[name] = False
        else:
            hours = " ".join(list(location.find_all("p")[2].stripped_strings))
            location_data[name] = hours
    for script in soup.find_all("script"):
        if "var mappangea5_data =" in script.text:
            location_list = json.loads((script.text.split("var mappangea5_data =")[1].split("};")[0] + "}").replace("'",'"').split('"locations":')[1].split("]")[0] + "{}]")[:-1]
            for i in range(len(location_list)):
                store_data = location_list[i]
                if location_data[store_data["phone"]] == False:
                    continue
                store = []
                store.append("https://limefreshmexicangrill.com")
                store.append(store_data["name"])
                store.append(store_data["address"])
                if "," in store_data["citystzip"]:
                    store.append(store_data["citystzip"].split(",")[0])
                    store_zip_split = re.findall("([0-9]{5})",store_data["citystzip"])
                    if store_zip_split:
                        store_zip = store_zip_split[0]
                    else:
                        store_zip = "<MISSING>"
                    state_split = re.findall("([A-Z]{2})",store_data["citystzip"])
                    if state_split:
                        state = state_split[0]
                    else:
                        state = "<MISSING>"
                    store.append(state)
                    store.append(store_zip)
                else:
                    store.append(store_data["citystzip"])
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(store_data["phone"])
                store.append("lime fresh mexican grill")
                store.append(store_data["location"]["lat"])
                store.append(store_data["location"]["lng"])
                store.append(location_data[store_data["phone"]])
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
