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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.bubbakoos.com/"
    r = session.get("https://www.bubbakoos.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"col-sm-6 col-md-4 col-lg-3"}):
        if location.find("a")["href"] == "location/":
            if location.find("a",{"href":re.compile("tel:")}) == None:
                phone = "<MISSING>"
            else:
                phone = location.find("a",{"href":re.compile("tel:")}).text.strip().replace("TACO","8226")
            name = location.find("a").text
            address = " ".join(list(location.find_all("p")[0].stripped_strings))
            store_zip = " ".join(list(location.find_all("p")[2].stripped_strings))
            store = []
            store.append("https://www.bubbakoos.com")
            store.append(name)
            store.append(address)
            store.append(name.split(",")[0])
            store.append(name.split(",")[1])
            store.append(store_zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("bubbakoo's burrito's")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            yield store
        else:
            location_request = session.get(base_url + location.find("a")["href"],headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            name = location.find("a").text
            if location_soup.find("a",{"href":re.compile("tel:")}) == None:
                phone = "<MISSING>"
            else:
                phone = location_soup.find("a",{"href":re.compile("tel:")}).text.strip().replace("TACO","8226")
            hours = " ".join(list(location_soup.find("div",{"class":'contact_details_sec'}).find_all("p")[5].stripped_strings))
            if hours == "":
               hours = " ".join(list(location_soup.find("div",{"class":'contact_details_sec'}).find_all("p")[4].stripped_strings)) 
            address = " ".join(list(location.find_all("p")[0].stripped_strings))
            store_zip = " ".join(list(location.find_all("p")[2].stripped_strings))
            if store_zip == "":
                address = " ".join(list(location.find_all("p")[1].stripped_strings))
                store_zip = " ".join(list(location.find_all("p")[3].stripped_strings))
            city_state = " ".join(list(location_soup.find("div",{"class":'contact_details_sec'}).find_all("p")[0].stripped_strings))
            store = []
            store.append("https://www.bubbakoos.com")
            store.append(name)
            store.append(address)
            store.append(city_state.split(",")[0])
            store.append(city_state.split(",")[1])
            if store[-2] in store[-3]:
                store[-3] = store[-3].replace(store[-2],"").replace(store[-1],"").replace(",","")
            store.append(store_zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("bubbakoo's burrito's")
            if location_soup.find("iframe") == None:
                store.append("<MISSING>")
                store.append("<MISSING>")
            else:
                geo_location = location_soup.find("iframe")["src"]
                store.append(geo_location.split("!3d")[1].split("!")[0])
                store.append(geo_location.split("!2d")[1].split("!")[0])
            store.append(hours.replace("–","-") if hours != "" else "<MISSING>")
            store.append(base_url + location.find("a")["href"])
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
