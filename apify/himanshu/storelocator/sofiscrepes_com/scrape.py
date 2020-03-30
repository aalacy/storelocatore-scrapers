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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    print("soup ===  first")

    base_url = "https://www.sofiscrepes.com"
    r = session.get("http://sofiscrepes.com/locations/", headers=headers)
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
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "sofiscrepes"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    list_hours = []
    for script_hours in soup.find_all("div", {"class": "answer"}):
        list_hours.append(" ".join(list(script_hours.stripped_strings)))
    # print("script_hours ===== "+str(list_hours))

    for script_bloc in soup.find_all("div", {"class": re.compile("addressblock")}):
        for script in script_bloc.find_all("div", {"class": re.compile("address")}):
            address_list = list(script.stripped_strings)

            if 'Fells Point' in address_list:
                address_list.remove('Fells Point')

            # print("address_list ===== "+str(address_list))
            street_address = address_list[0]

            try:
                phone = address_list[2]
                city = address_list[1].split(",")[0]
                state = address_list[1].split(",")[1].strip().split(" ")[0]
                zipp = address_list[1].split(",")[1].strip().split(" ")[1]
            except:
                phone = address_list[1]
                city = address_list[2].split(",")[0]
                state = address_list[2].split(",")[1].strip().split(" ")[0]
                zipp = address_list[2].split(",")[1].strip().split(" ")[1]

            location_name = city
            hours_of_operation = list_hours[len(return_main_object)]
            # it will remove if specific word contain in string of list then  it will remove that element.
            # address_list = [x for x in address_list if "Suite" not in x]
            # address_list = [x for x in address_list if "Unit" not in x]

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
