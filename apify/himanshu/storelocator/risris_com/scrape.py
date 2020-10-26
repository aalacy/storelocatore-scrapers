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

    base_url = "https://www.risris.com"
    r = session.get("http://www.risris.com/contact", headers=headers)
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
    location_type = "risris"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for script in soup.find_all("div", {"class": "sfContentBlock"}):
        address_list = list(script.stripped_strings)

        for i in range(len(address_list)):
            address_list[i] = re.sub('[^A-Za-z0-9 ]+', '', address_list[i])

        # it will remove if specific word contain in string of list then  it will remove that element.
        # address_list = [x for x in address_list if "Suite" not in x]
        # address_list = [x for x in address_list if "Unit" not in x]

        if "Location" in address_list:
            # print("address_list ==== "+str(address_list))

            location_name = address_list[0]
            street_address = address_list[1]
            phone = address_list[3].replace("Phone", "").strip()
            if phone.isdigit():
                pass
            else:
                phone = "<MISSING>"

            if len(address_list[2].split(" ")[-1][-5:]) == 5:
                city = " ".join(address_list[2].split(" ")[:-2])
                state = address_list[2].split(" ")[-2]
                zipp = address_list[2].split(" ")[-1]
            else:
                street_address += " "+ address_list[2]
                city = " ".join(address_list[3].split(" ")[:-2])
                state = address_list[3].split(" ")[-2]
                zipp = address_list[3].split(" ")[-1]

            if len(zipp) > 5:
                state = zipp[:-5]
                zipp = zipp[-5:]
                city = " ".join(address_list[2].split(" ")[:-1])

            map_location = script.find('a')["href"]
            if len(map_location.split("&sll=")) > 1:
                latitude = map_location.split("&sll=")[1].split("&")[0].split(",")[0]
                longitude = map_location.split("&sll=")[1].split("&")[0].split(",")[1]
            elif len(map_location.split("/@")) > 1:
                latitude = map_location.split("/@")[1].split(",")[0]
                longitude = map_location.split("/@")[1].split(",")[1]
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            # print("map_location ==== "+map_location)
            # print("longitude ==== "+longitude)
            # print("latitude ==== "+latitude)

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
