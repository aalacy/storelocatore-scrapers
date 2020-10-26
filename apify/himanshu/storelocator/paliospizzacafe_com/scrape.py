import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import html


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.paliospizzacafe.com"
    r = session.get("https://www.paliospizzacafe.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("store").find_all("item"):
        name = location.find("location").text
        address = location.find("address").text.split(",")[0].split("  ")[0]
        city = location.find("address").text.split(",")[0].split("  ")[1]
        state = location.find("address").text.split(",")[1].split(" ")[-2]
        zip_code = location.find("address").text.split(",")[1].split(" ")[-1]
        phone = location.find("telephone").text
        country = "US"
        lat = location.find("latitude").text
        lng = location.find("longitude").text
        store_id = location.find("storeid").text
        location_url = BeautifulSoup(location.find("description").text,"lxml").find("a",text="More Info")["href"]
        location_request = session.get(location_url,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        hours = " ".join(list(location_soup.find("span",text=re.compile("HOURS")).parent.parent.parent.find_next_sibling('div').stripped_strings))
        store = []
        store.append("https://www.paliospizzacafe.com")
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip_code)
        store.append(country)
        store.append(store_id)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(location_url)
        for i in range(len(store)):
            store[i] = html.unescape(store[i])
        print(store)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
