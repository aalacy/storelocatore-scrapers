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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.diptyqueparis.com"
    r = session.get("https://www.diptyqueparis.com/en_us/cms/page/view/page_id/19",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for country in soup.find_all("div",{"class":"widget block block-static-block full_width tc-paragraph faq-paragraph"}):
        if "United States" in  country.find("h2").text:
            states = country.find("div",{'class':"block-cms-text"}).find_all("h3")
            locations = country.find("div",{'class':"block-cms-text"}).find_all("table")
            for i in range(len(states)):
                for location in locations[i].find_all("td"):
                    location_details = list(location.stripped_strings)
                    if location_details == []:
                        continue
                    store = []
                    store.append("https://www.diptyqueparis.com")
                    store.append(location_details[0])
                    if (len(location_details[2].split(" ")) == 3 or len(location_details[2].split(" ")) == 4 or len(location_details[2].split(" ")) == 5) and location_details[2].split(" ")[0].isdigit():
                        store.append(location_details[1])
                        store.append(" ".join(location_details[2].split(" ")[1:-1]))
                        store.append(states[i].text)
                        store.append(location_details[2].split(" ")[0])
                    elif len(location_details) > 4 and len(location_details[4].split(" ")[0]) == 5 and location_details[4].split(" ")[0].isdigit():
                        store.append(" ".join(location_details[1:4]))
                        store.append(" ".join(location_details[4].split(" ")[1:-1]))
                        store.append(states[i].text)
                        store.append(location_details[4].split(" ")[0])
                    else:
                        store.append(" ".join(location_details[1:3]))
                        store.append(" ".join(location_details[3].split(" ")[1:-1]))
                        store.append(states[i].text)
                        store.append(location_details[3].split(" ")[0])
                    store.append("US")
                    store.append("<MISSING>")
                    for k in range(len(location_details)):
                        if "(" in location_details[k] and ")" in location_details[k] and len(location_details[k]) < 20:
                            store.append(location_details[k])
                            break
                    if len(store) == 8:
                        store.append("<MISSING>")
                    store.append("dipt qyue")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(" ".join(location_details[4:]) if len(location_details) > 4 else " ".join(location_details[3:]))
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
