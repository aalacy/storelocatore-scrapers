import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    # print("soup ===  first")

    base_url = "https://vmaretail.secure-decoration.com"
    r = session.get("https://vmaretail.secure-decoration.com/contact", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "https://vmaretail.secure-decoration.com/contact"
    # for script in soup.find_all("a", {"onclick": re.compile("focus_and_popup")}):
    address_list = list(soup.find('div',{"id":"995e3e96-470f-4b12-9bb9-aebe488821ac_text"}).stripped_strings)
    # print("address_list ==== "+str(address_list))

    street_address = address_list[1]
    zipp = address_list[2]
    city = address_list[3]
    location_name = city
    state = address_list[4]
    country_code = "US"
    phone = soup.find("div",{"class":"dn-phone-number"}).text


    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
             store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

    # print("data = " + str(store))
    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    return_main_object.append(store)

    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
