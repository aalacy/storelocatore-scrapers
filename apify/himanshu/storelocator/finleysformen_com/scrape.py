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
    base_url = "http://finleysformen.com"
    r = session.get("http://finleysformen.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("li",{"data-grids-item":""}):
        if location.find("span") == None:
            continue
        if "data-content" not in location.find("span").attrs:
            continue
        location_soup = BeautifulSoup(location.find("span")["data-content"],"lxml")
        location_list = list(location_soup.find("div",{'class':"location-details"}).stripped_strings)
        for i in range(len(location_list)):
            if "GET DIRECTIONS" == location_list[i]:
                location_list = location_list[:i]
                break
        if len(location_list[2].split(",")) == 1:
            location_list[1] = " ".join(location_list[1:3])
            del location_list[2]
        if location_soup.find("a",{"href":re.compile("/@")}) == None:
            lat = "<INACCESSIBLE>"
            lng = "<INACCESSIBLE>"
        else:
            lat = location_soup.find("a",{"href":re.compile("/@")})["href"].split("/@")[1].split(",")[0]
            lng = location_soup.find("a",{"href":re.compile("/@")})["href"].split("/@")[1].split(",")[1]
        store = []
        store.append("http://finleysformen.com")
        store.append(location_list[0])
        store.append(location_list[1])
        store.append(location_list[2].split(",")[0])
        store.append(location_list[2].split(",")[1].split(" ")[-2])
        store.append(location_list[2].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_list[3])
        store.append("finley's barber shop")
        store.append(lat)
        store.append(lng)
        store.append(" ".join(location_list[4:-1]))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
