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

    base_url = "https://www.hueymagoos.com"
    r = session.get("https://hueymagoos.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<INACCESSIBLE>"
    city = "<INACCESSIBLE>"
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "hueymagoos"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # print("data ====== "+str(soup))
    for script in soup.find_all("div", {"class": "wpb_column vc_column_container vc_col-sm-6"}):

        script_location = script.find_all("div", {"class": "mkdf-icon-list-item"})

        if len(script_location) > 2:
            phone = "".join(list(script_location[0].stripped_strings))
            address_list = list(script_location[1].stripped_strings)
            hours_of_operation = "".join(list(script_location[2].stripped_strings)) +","+ "".join(list(script_location[3].stripped_strings))

            # print("address_list ==== "+ str(address_list))
            if len(address_list[0].split(',')) > 2:
                street_address = address_list[0].split(',')[0]
                city = address_list[0].split(',')[-2]
                state = "".join(address_list[0].split('.')[-1]).split(",")[-1].strip().split(' ')[0]
                zipp = "".join(address_list[0].split('.')[-1]).split(",")[-1].strip().split(' ')[1]
            else:
                street_address = " ".join(address_list[0].split('.')[:-1])
                city = "".join(address_list[0].split('.')[-1]).split(",")[0]
                state = "".join(address_list[0].split('.')[-1]).split(",")[1].strip().split(' ')[0]
                zipp = "".join(address_list[0].split('.')[-1]).split(",")[1].strip().split(' ')[1]

            country_code = "US"

            location_name = city
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)

        else:
            if "Coming Soon" != "".join(list(script_location[0].stripped_strings)):
                # print("else =================== "+ str(list(script_location[0].stripped_strings)))
                address_list = list(script_location[0].stripped_strings)
                hours_of_operation = "".join(list(script_location[1].stripped_strings))
                if len(address_list[0].split(',')) > 2:
                    street_address = address_list[0].split(',')[0]
                    city = address_list[0].split(',')[-2]
                    state = "".join(address_list[0].split('.')[-1]).split(",")[-1].strip().split(' ')[0]
                    zipp = "".join(address_list[0].split('.')[-1]).split(",")[-1].strip().split(' ')[1]
                else:
                    street_address = " ".join(address_list[0].split('.')[:-1])
                    city = "".join(address_list[0].split('.')[-1]).split(",")[0]
                    state = "".join(address_list[0].split('.')[-1]).split(",")[1].strip().split(' ')[0]
                    zipp = "".join(address_list[0].split('.')[-1]).split(",")[1].strip().split(' ')[1]

                location_name = city
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
            else:
                street_address = "<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
                hours_of_operation = "<MISSING>"
            phone = "<MISSING>"



    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
