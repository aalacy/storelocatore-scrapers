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
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    base_url = "https://bodyalivefitness.com"
    r = session.get(base_url,headers=header)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    menu = soup.find("ul",{"id":"top-menu"}).find("ul",{"class":"sub-menu"})
    for location in menu.find_all("li",{"id":re.compile("menu-item-")}):
        link = location.find("a")["href"]
        location_request = session.get(link,headers=header)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("div",{"class":"et_pb_text_inner"}).stripped_strings)
        store = []
        store.append("https://bodyalivefitness.com")
        store.append(location_details[0])
        if location_details[1] == "(Coming Soon)":
            store.append(" ".join(location_details[2].split(",")[0].split(" ")[0:-2]))
            store.append(" ".join(location_details[2].split(",")[0].split(" ")[-2:]))
            store.append(location_details[2].split(",")[-1].split(" ")[-2])
            store.append(location_details[2].split(",")[-1].split(" ")[-1])
        else:
            store.append(location_details[1].split(".")[0])
            store.append(location_details[1].split(".")[1].split(",")[0])
            store.append(location_details[1].split(",")[-1].split(" ")[-2])
            store.append(location_details[1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append(location['id'].split("menu-item-")[1])
        if location_details[1] == "(Coming Soon)":
            store.append("<MISSING>")
        else:
            store.append(location_details[2])
        store.append("body alive")
        store.append(location_soup.find("iframe")["src"].split("!3d")[1].split("!")[0])
        store.append(location_soup.find("iframe")["src"].split("!2d")[1].split("!")[0])
        store.append("<INACCESSIBLE>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
