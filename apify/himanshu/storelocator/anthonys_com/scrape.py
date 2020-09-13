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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    addresses = []

    base_url = "https://www.anthonys.com"
    r = session.get("https://www.anthonys.com/reservations/", headers=headers)
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
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for script_reservation in soup.find_all("div", {"class": "text"}):

        for script_reservation_a in script_reservation.find_all('a'):
            link = script_reservation_a['href']
            r_location = session.get(link, headers=headers)
            soup_location = BeautifulSoup(r_location.text, "lxml")

            for script in soup_location.find_all('div', {'id': 'contentbody'}):
                address_list = list(script.stripped_strings)

                street_address = address_list[1]
                city = address_list[2].split(',')[0]
                state = address_list[2].split(',')[1].strip().split(' ')[0]
                zipp = address_list[2].split(',')[1].strip().split(' ')[-1]
                phone = address_list[4].replace("PH:", "").strip()
                hours_of_operation = script.h3.text.replace("Hours:","").replace("\r\n\t"," ").strip()
                if "pm" not in hours_of_operation.lower():
                    raw_hours = soup_location.find(id="intro").find_all("p")[1].text.strip().split("\n")[1]
                    hours_of_operation = raw_hours[raw_hours.find(":")+1:].strip()
                location_name = soup_location.find(id="stylized").text.strip()

                store = [locator_domain, link, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation.replace(",","")]

                if str(store[2]) + str(store[-3]) not in addresses:
                    addresses.append(str(store[2]) + str(store[-3]))

                    store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
