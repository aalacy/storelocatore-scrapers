import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pioneerbnk_com')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.pioneerbnk.com"
    r = session.get("https://www.pioneerbnk.com/locations-hours/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")

    return_main_object = []
    links = soup.find(class_="post-content").find_all("a")

    for i in links:
        link = i["href"]
        # logger.info(link)

        r = session.get(link,headers=headers)
        location = BeautifulSoup(r.text,"lxml")

        location_details = list(location.find_all("div",{"class":"fusion-text"})[-1].stripped_strings)
        store = []
        store.append("https://www.pioneerbnk.com")
        store.append(link)
        store.append(location_details[0])
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store.append(location_details[1].split(",")[1].split(" ")[-2])
        store.append(location_details[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        for i in range(len(location_details)):
            if "Phone:" in location_details[i]:
                phone = location_details[i].split("Phone:")[1].replace(",","").replace(";","")
        hours = ""
        for i in range(len(location_details)):
            if "Hour" in location_details[i]:
                hours = " ".join(location_details[i:])
                break
        if "Lobby" in hours:
            hours = hours[hours.find("Lobby"):hours.find("Drive")].replace("Lobby Hours","").replace(":","").strip()
        store.append(phone)
        location_type = "Bank"
        if "atm" in hours.lower():
            location_type = "ATM"
        if "corporate" in link:
            location_type = "Corporate Headquarters"
        store.append(location_type)
        map_link = location.find(class_="fusion-no-lightbox")["href"]
        at_pos = map_link.rfind("@")
        lat = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
        lng = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
        store.append(lat)
        store.append(lng)
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
