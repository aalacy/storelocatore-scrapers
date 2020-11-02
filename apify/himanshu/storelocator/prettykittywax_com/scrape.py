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
    base_url = "https://prettykittywax.com"
    r = session.get("https://prettykittywax.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    address = []
    for location in soup.find("div",{"class":"popup"}).find_all("a"):
        if len(location['href'].split("/")[-2]) == 2:
            continue
        location_request = session.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,'lxml')
        location_details = []
        for details in location_soup.find_all("div",{"class":"vc_column_container vc_col-sm-4"}):
            location_details.extend(list(details.stripped_strings))
        if "CALL TO BOOK APPOINTMENT:" == location_details[3]:
            location_details[0] = location_details[0:2]
            del location_details[1]
        phone = location_soup.find("a",{"href":re.compile("tel:")}).text
        store = []
        store.append("https://prettykittywax.com")
        store.append(location["href"].split("/")[-2])
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store.append(location_details[1].split(",")[-1].split(" ")[-2])
        store.append(location_details[1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("pretty kitty wax")
        for script in location_soup.find_all("script"):
            if "new google.maps.LatLng(" in script.text:
                lat = script.text.split("new google.maps.LatLng(")[1].split(",")[0]
                lng = script.text.split("new google.maps.LatLng(")[1].split(",")[1].split(")")[0]
        store.append(lat)
        store.append(lng)
        store.append(" ".join(location_details[3:]))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
