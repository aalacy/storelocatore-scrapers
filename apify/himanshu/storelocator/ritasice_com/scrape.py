import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}
session = SgRequests()

def fetch_data():
    return_main_object = []
    addresses = []
    MAX_RESULTS = 19
    search = sgzip.ClosestNSearch()
    search.initialize()
    coord = search.next_coord()
    while coord:
        result_coords = []
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        r = session.get("https://www.ritasice.com/wp-admin/admin-ajax.php?action=ritas_store_locator_function&latitude=" + str(x) + "&longitude="+ str(y),headers=HEADERS)
        soup = BeautifulSoup(r.text,"lxml")
        for script in soup.find_all("script"):
            if "var locations = " in script.text:
                json_text = (script.text.split("var locations = ")[1].split("];")[0] + "]").replace("'",'"')
                if json_text[-2] == ",":
                    json_text = json_text[:-2] + json_text[-1:]
                location_list = json.loads(json_text)
                for location in location_list:
                    location_request = session.get("https://www.ritasice.com/wp-admin/admin-ajax.php?action=ritas_store_detail_function&id=" + str(location[-1]),headers=HEADERS)
                    location_soup = BeautifulSoup(location_request.text,"lxml")
                    name = location_soup.find("h4",{"class":"location-name"}).text.strip()
                    address = location_soup.find("span",{'class':"address"}).text.strip()
                    street_address = address.split(",")[0]
                    city = address.split(",")[1]
                    state = re.findall("([A-Z]{2})",address)[-1]
                    store_zip_split = re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",address)
                    if store_zip_split:
                        store_zip = store_zip_split[-1]
                    else:
                        store_zip = "<MISSING>"
                    store_id = location[-1]
                    phone = location_soup.find("a",{'href':re.compile("tel:")}).text.strip()
                    hours = " ".join(list(location_soup.find("div",{"id":"collapseHours"}).stripped_strings))
                    lat = location[1]
                    lng = location[2]
                    result_coords.append((lat, lng))
                    page_url = "https://www.ritasice.com/wp-admin/admin-ajax.php?action=ritas_store_detail_function&id=" + str(location[-1])            
                    store = []
                    store.append("https://www.ritasice.com")
                    store.append(name)
                    store.append(street_address)
                    if store[-1] in addresses:
                        continue
                    addresses.append(store[-1])
                    store.append(city.strip())
                    store.append(state)
                    store.append(store_zip)
                    store.append("US")
                    store.append(store_id)
                    store.append(phone if phone else "<MISSING>")
                    store.append("<MISSING>")
                    store.append(lat)
                    store.append(lng)
                    store.append(hours if hours != "" else "<MISSING>")
                    if store[-1].count("CLOSED") > 12:
                        continue
                    store.append(page_url)
                    yield store
        search.max_count_update(result_coords)
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
