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
    base_url = "https://www.signaturestyle.com/brands/first-choice-haircutters.html"
    r = requests.get("https://www.signaturestyle.com/salon-directory.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    divs = soup.find("div",{'class':"content parsys"}).find_all("div",recursive=False)[1:]
    for i in range(0,len(divs),2):
        country = ""
        if "U.S." in list(divs[i].stripped_strings)[0] or "Canada" in list(divs[i].stripped_strings)[0]:
            if "U.S." in list(divs[i].stripped_strings)[0]:
                country = "US"
            else:
                country = "CA"
            for state in divs[i+1].find_all("a",{"class":"btn btn-primary"}):
                state_request = requests.get("https://www.signaturestyle.com" + state["href"],headers=headers)
                state_soup = BeautifulSoup(state_request.text,"lxml")
                for table in state_soup.find_all("table"):
                    for location in table.find_all("a"):
                        location_request = requests.get("https://www.signaturestyle.com" + location["href"],headers=headers)
                        location_soup = BeautifulSoup(location_request.text,"lxml")
                        if location_soup.find("div",{'class':"h2 h3"}) == None:
                            continue
                        name = " ".join(list(location_soup.find("div",{'class':"h2 h3"}).stripped_strings))
                        street_address = " ".join(list(location_soup.find("span",{'itemprop':"streetAddress"}).stripped_strings))
                        city = location_soup.find("span",{'itemprop':"addressLocality"}).text
                        state = location_soup.find("span",{'itemprop':"addressRegion"}).text
                        store_zip = location_soup.find("span",{'itemprop':"postalCode"}).text
                        phone = location_soup.find("span",{'itemprop':"telephone"}).text
                        hours = " ".join(list(location_soup.find("div",{'class':"salon-timings"}).stripped_strings))
                        lat = location_soup.find("meta",{'itemprop':"latitude"})["content"]
                        lng = location_soup.find("meta",{'itemprop':"longitude"})["content"]
                        store = []
                        store.append("https://www.signaturestyle.com")
                        store.append(name.replace("\xa0"," "))
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(store_zip)
                        store.append(country)
                        store.append("<MISSING>")
                        store.append(phone if phone != "" else "<MISSING>")
                        store.append("signature style")
                        store.append(lat)
                        store.append(lng)
                        store.append(hours if hours != "" else "<MISSING>")
                        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
