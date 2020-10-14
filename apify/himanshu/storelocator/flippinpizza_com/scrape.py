import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }

    soup = bs(session.get("https://flippinpizza.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php",headers=headers).text,"lxml")
    
    for location in soup.find_all("item"):
        name = location.find("location").text.replace("&#44;",",")
        address = list(bs(location.find("description").text,"lxml").find("div").stripped_strings)
        phone = location.find("telephone").text
        lat = location.find("latitude").text
        lng = location.find("longitude").text
        location_url = bs(location.find("description").text,"lxml").find_all("a")[-1]["href"]
        location_request = session.get(location_url,headers=headers)
        location_soup = bs(location_request.text,"lxml")
        yelp_url = location_soup.find("a",text="Yelp")["href"]
       
        yelp_request = session.get(yelp_url,headers=headers)
        yelp_soup = bs(yelp_request.text,"lxml")

        hours = " ".join(list(yelp_soup.find("p",text="Mon").parent.parent.parent.stripped_strings))
        
        store = []
        store.append("https://flippinpizza.com")
        store.append(name)
        store.append(" ".join(address[:-1]))
        store.append(address[-1].split(",")[0])
        store.append(address[-1].split(",")[1].split(" ")[-2])
        store.append(address[-1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone != "" else "<MISSING>")
        store.append("flippin' pizza")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(location_url)

        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

