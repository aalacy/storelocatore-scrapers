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

    base_url = "https://www.sageveganbistro.com"
    r = session.get("https://www.sageveganbistro.com/our-story/#locations", headers=headers)
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
    location_type = "sageveganbistro"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # print("data ==== "+str(soup))

    for script in soup.find_all("div", {"class": "sqs-block-content"}):
        for script1 in script.find_all("p", {"style": "white-space:pre-wrap;"}):

            address_list = list(script.stripped_strings)

            if 'RESERVE' in address_list:
                address_list.remove('RESERVE')

            if 'ORDER' in address_list:
                address_list.remove('ORDER')

            if 'PRIVATE DINING' in address_list:
                address_list.remove('PRIVATE DINING')

            if '\ufeff' in address_list:
                address_list.remove('\ufeff')

            if '|' in address_list:
                address_list.remove('|')

            if '|' in address_list:
                address_list.remove('|')

            if len(address_list) > 0:

                location_name = address_list[0]
                street_address = address_list[1]
                city = address_list[2].split(',')[0]
                state = address_list[2].split(',')[1].strip().split(' ')[0]
                zipp = address_list[2].split(',')[1].strip().split(' ')[1]
                phone = address_list[-1]

                print("address_list === " + str(address_list))
                # print("location_url === "+location_url)

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]

                print("data = " + str(store))
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
