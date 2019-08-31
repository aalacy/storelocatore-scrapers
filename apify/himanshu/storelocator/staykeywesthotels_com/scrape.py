import csv
import requests
from bs4 import BeautifulSoup
import re
import json

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
    base_url = "https://www.staykeywesthotels.com"
    r = requests.get("https://www.staykeywesthotels.com/wp-admin/admin-ajax.php?action=get_states_cities",headers=headers)
    data = r.json()
    return_main_object = []
    for state in data:
        for city in data[state]["properties"]:
            location_request = requests.get(data[state]["properties"][city]["link"])
            location_soup = BeautifulSoup(location_request.text,"lxml")
            store_name = "".join(list(location_soup.find("h2",{'class':'cobble-font'}).stripped_strings))
            store_city = store_name.split(",")[0]
            store_state = store_name.split(",")[-1]
            store_address = location_soup.find("address",{'class':"address"}).text.split(",")[0].replace(store_city,"")
            store_zip = location_soup.find("address",{'class':"address"}).text.split(",")[-1].split(" ")[2]
            for script in location_soup.find_all("script"):
                if '"latitude"' in script.text:
                    lat = script.text.split('"latitude":')[1].split(",")[0].replace('"',"")
                    lng = script.text.split('"longitude":')[1].split("}")[0].replace('"',"")
            phone = location_soup.find("a",{'href':re.compile("tel:")}).text.strip()
            hours = ""
            if location_soup.find("li",{'class':"contact-checkin"}) != None:
                hours = hours + " " + location_soup.find("li",{'class':"contact-checkin"}).text.strip()
            if location_soup.find("li",{'class':"contact-checkout"}) != None:
                hours = hours + " " + location_soup.find("li",{'class':"contact-checkout"}).text.strip()
            store = []
            store.append("https://www.staykeywesthotels.com")
            store.append(store_name)
            store.append(store_address if store_address != "" and store_address != " " else "<MISSING>")
            store.append(store_city if store_city != "" else "<MISSING>")
            store.append(store_state if store_state != "" else "<MISSING>")
            store.append(store_zip if store_zip != "" else "<MISSING>")
            store.append("US")
            store.append(data[state]["properties"][city]["page_id"])
            store.append(phone if phone != "" else "<MISSING>")
            store.append("quicklyusa")
            store.append(lat if lat != "" else "<MISSING>")
            store.append(lng if lng != "" else "<MISSING>")
            store.append(hours if hours != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
