import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    base_url = "https://emackandbolios.com"
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "https://emackandbolios.com/locations/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    r = session.get("https://emackandbolios.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    content = soup.find("section", {"id": "usa"})
    for div in content.find_all("div", class_="elementor-text-editor")[:-1]:
        list_add = list(div.stripped_strings)
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_add[-1]))
        location_name = list_add[0]
        if len(list_add) > 3:
            street_address = " ".join(list_add[1:-2]).strip()
            city = list_add[2].split(',')[0].strip()
            state = list_add[2].split(',')[-1].strip()
        elif len(list_add)==2:
            street_address = list_add[0]
            city = list_add[1].split(',')[0].strip()
            state = list_add[1].split(',')[-1].strip()
        else:
            if phone_list:
                street_address = "<MISSING>"
                city = list_add[1].split(',')[0].strip()
                state = list_add[1].split(',')[-1].strip()
            else:
                street_address = list_add[1].strip()
                city = list_add[2].split(',')[0].strip()
                state = list_add[2].split(',')[-1].strip()
        if phone_list:
            phone = phone_list[0].strip()
        else:
            phone = "<MISSING>"
        if "Coming Soon" in location_name:
            continue
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = ["<MISSING>" if x == "" else x for x in store]
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
