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
    base_url = "https://www.audiusa.com"
    r = session.get(base_url + "/dealers-webapp/map")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []

    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if "window.Audi.Vars.dealers" in script.text:
            location_list = json.loads(script.text.split("window.Audi.Vars.dealers = ")[1].split("];")[0] + "]")
            for i in range(len(location_list)):
                current_store = location_list[i]
                store = []
                store.append("https://www.audiusa.com")
                store.append(current_store["name"])
                store.append(current_store["address1"])
                store.append(current_store["city"])
                store.append(current_store["state"])
                store.append(current_store["zip"])
                store.append("US")  
                store.append(current_store["id"])
                store.append(current_store["phone"])
                department_id = 0
                open_hours = ""
                for k in range(len(current_store["departments"])):
                    if current_store["departments"][k]["departmentCode"] == "SALES":
                        for j in range(len(current_store["departments"][k]["hoursOfOperation"])):
                            hoursOfOperation = current_store['departments'][k]["hoursOfOperation"]
                            if hoursOfOperation[j]["closedIndicator"] == "N":
                                open_hours = open_hours + hoursOfOperation[j]["name"] + " openTime " + hoursOfOperation[j]['hours'][0]["openTime"] + " closeTime " + hoursOfOperation[j]['hours'][0]["closeTime"] + " "
                        department_id = k
                        break
                store.append("audi" + " " + current_store['departments'][k]["departmentCode"])
                store.append(current_store["latitude"])
                store.append(current_store["longitude"])
                if open_hours == "":
                    pass
                else:
                    store.append(open_hours)
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
