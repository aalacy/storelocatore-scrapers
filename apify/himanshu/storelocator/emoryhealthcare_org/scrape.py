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
    data = '{"selectFields":["Name","Address","City","State","Zip","URL","Type","Specialists","Latitude","Longitude"],"filters":{},"geoWithin":{},"orderBy":{"Name":-1}}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'Host': "www.emoryhealthcare.org",
        "Origin": "https://www.emoryhealthcare.org",
        "Referer": "https://www.emoryhealthcare.org/locations/index.html?type=primary",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    base_url = "https://www.emoryhealthcare.org"

    r = session.post("https://www.emoryhealthcare.org/service/findPhysician/api/locations/retrieve",headers=headers,data=data,verify=False)
    phone_request = session.get("https://www.emoryhealthcare.org/locations/index.html?type=primary#map",verify=False)
    phone_soup = BeautifulSoup(phone_request.text,"lxml")
    phone = phone_soup.find("li",{'class':"hidden-xs"}).find_all("a")[-1].text
    data = r.json()["locations"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.emoryhealthcare.org")
        store.append(store_data['NAME'])
        store.append(store_data["ADDRESS"])
        store.append(store_data['CITY'])
        store.append(store_data['STATE'])
        store.append(store_data["ZIP"])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("emory healthcare")
        store.append(store_data["LATITUDE"])
        store.append(store_data["LONGITUDE"])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
