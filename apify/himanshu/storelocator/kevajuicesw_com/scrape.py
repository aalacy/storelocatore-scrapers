import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


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
    base_url = "http://www.kevajuicesw.com"
    r = session.get(base_url + "/locations")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    parts = soup.find("div",{"class": "entry-content content"})
    for semi_parts in parts.find_all("div",{"class": re.compile("x-column one")}):
        # print(semi_parts)
        p_tags = semi_parts.find_all("p")
        if p_tags == []:
            continue
        name = list(p_tags[0].stripped_strings)[0]
        lcoation_details = list(p_tags[1].stripped_strings)
        location_hours = list(p_tags[2].stripped_strings)
        if len(lcoation_details) > 3:
            lcoation_details = lcoation_details[1:]
        store = []
        store.append("http://www.kevajuicesw.com")
        store.append(name)
        store.append(lcoation_details[0])
        if len(lcoation_details) == 1:
            continue
        # else:
        store.append(lcoation_details[1].split(",")[0])
        if len(lcoation_details[1].split(",")) > 2:
            store[-2] = store[-2] + lcoation_details[1].split(",")[0]
            store[-1] = lcoation_details[1].split(",")[1]
            store.append(lcoation_details[1].split(",")[2].split(" ")[-2])
            store.append(lcoation_details[1].split(",")[2].split(" ")[-1])
        elif len(lcoation_details[1].split(",")[1].split(" ")) == 2:
            store.append(lcoation_details[1].split(",")[1].split(" ")[-1])
            store.append("<MISSING>")
        else:
            store.append(lcoation_details[1].split(",")[1].split(" ")[-2])
            store.append(lcoation_details[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append(name.split("#")[1].split(" ")[0])
        store.append(lcoation_details[-1] if len(lcoation_details) == 3 else location_hours[0])
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        hours = " ".join(location_hours) if len(lcoation_details) == 3 else " ".join(list(p_tags[3].stripped_strings))
        if "Temporary Closed" in hours :
            hours = "<MISSING>"
        final_hours = (hours.replace("Hours ","").replace("(Drive Thru Only)",""))
        store.append(final_hours)
        store.append("http://www.kevajuicesw.com/locations/")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
