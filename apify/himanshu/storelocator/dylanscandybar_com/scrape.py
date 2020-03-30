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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","raw_address"])
        # Body
        for row in data:
            print(row)
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.dylanscandybar.com"
    r = session.get(base_url + "/Store-Locator")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("li",{"class":"store"}):
        name = location.find("h3",{"class":"store-title"}).text
        location_details = location.find("div",{"class":"store-contacts-entry"})
        lcoation_hours = list(BeautifulSoup(location_details.prettify().split("<h6>")[1],"lxml").stripped_strings)
        location_details = list(BeautifulSoup(location_details.prettify().split("<h6>")[2],"lxml").stripped_strings)
        lat = "<MISSING>"
        lng = "<MISSING>"
        if location_details[-1] == "View on map":
            del location_details[-1]
            geo_location = location.find_all('a')[3]["href"]
            if len(geo_location.split("@")) > 1:
                lat = geo_location.split("/@")[1].split(",")[0]
                lng = geo_location.split("/@")[1].split(",")[1]
            else:
                lat = "<INACCESSIBLE>"
                lng = "<INACCESSIBLE>"
        phone = ""
        for i in range(len(location_details)):
            if location_details[i].replace("(Main Hotel)","").replace("*Accessible only to Madame Tussauds NYC ticket holders","").replace(" ","").replace("(","").replace(")","").replace("-","").isdigit():
                phone = location_details[i].replace("(Main Hotel)","").replace("*Accessible only to Madame Tussauds NYC ticket holders","")
                del location_details[i]
                break
        if location_details[0] == "Location":
            del location_details[0]
        else:
            location_details[0] = location_details[0].split("Location")[1].replace("\n","")
        store = []
        store.append("https://www.dylanscandybar.com")
        store.append(name.replace("\u2003"," "))
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        zip_codes = []
        for i in range(len(location_details)):
            zip_1  = []
            zip_code = re.findall('\d+', location_details[i])
            for j in range(len(zip_code)):
                if len(str(zip_code[j])) == 5:
                    zip_1.append(zip_code[j])
            zip_codes.extend(zip_1)
        store.append(zip_codes[-1] if len(zip_codes) > 0 else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone != "" else "<MISSING>")
        store.append("dylan's candy bar")
        store.append(lat)
        store.append(lng)
        store.append(" ".join(lcoation_hours))
        store.append(" ".join(location_details))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
