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

    base_url = "https://www.pagliacci.com"
    r = session.get("https://www.pagliacci.com/locations/category/all", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find_all("div", {"class": "location_result"}):
        store_url = base_url + script.find('a')['href']
        r_store = session.get(store_url, headers=headers)
        soup_store = BeautifulSoup(r_store.text, "lxml")

        address = ",".join(list(soup_store.find("div", {"id": "location_address"}).stripped_strings))
        map_location = soup_store.find("h3", {"class": "mapit"}).find("a")['href']

        hours_of_operation = ",".join(list(soup_store.find("div", {"class": "fieldvalue"}).stripped_strings))
        state = address.split(",")[-1].split(" ")[1]
        zipp = address.split(",")[-1].split(" ")[2]
        city = address.split(",")[-2]
        street_address = address.split(",")[2]
        location_name = address.split(",")[1]
        country_code = "US"

        # print("sll location ====== " + str(len(map_location.split("&sll="))))

        if len(map_location.split("&sll=")) > 1:
            latitude = map_location.split("&sll=")[1].split("&")[0].split(",")[0]
            longitude = map_location.split("&sll=")[1].split("&")[0].split(",")[1]
        elif len(map_location.split("/@")) > 1:
            latitude = map_location.split("/@")[1].split(",")[0]
            longitude = map_location.split("/@")[1].split(",")[1]
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        # print("~~~~~~~~~~" + address)
        # print("locator_domain = " + locator_domain)
        # print("location_name = " + location_name)
        # print("street_address = " + street_address)
        # print("city = " + city)
        # print("state = " + state)
        # print("zipp = " + zipp)
        # print("country_code = " + country_code)
        # print("store_number = " + store_number)
        # print("phone = " + phone)
        # print("location_type = " + location_type)
        # print("latitude = " + latitude)
        # print("longitude = " + longitude)
        # print("hours_of_operation = " + hours_of_operation)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,store_url]
        store = [x.replace("–","-") for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
