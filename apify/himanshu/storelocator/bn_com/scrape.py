import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    for zip_code in zips:
        # print(zip_code)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
        }
        base_url = "https://www.bn.com"

        # zip_code = 11030
        try:
            r = session.get("https://stores.barnesandnoble.com/stores?page=0&size=1000000&searchText=" + str(
            zip_code) + "+&storeFilter=all&view=list&v=1", headers=headers)
        except:
            continue
        soup = BeautifulSoup(r.text, "lxml")

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
        page_url = "<MISSING>"

        for script in soup.find_all("div", {"class": "col-md-7 col-lg-7 col-sm-7 col-xs-7"}):
            location_url = "https://stores.barnesandnoble.com" + \
                script.find('a')['href']
            page_url = location_url
            # print("location_url === " + str(location_url))

            r_location = session.get(location_url, headers=headers)
            soup_location = BeautifulSoup(r_location.text, "lxml")
            try:
                address_list = soup_location.find(
                    'div', {'class': 'col-sm-8 col-md-4 col-lg-4 col-xs-6'})
                location_name = address_list.find("h4").text.strip()
            except:
                location_name = "<MISSING>"
            # print(location_name)
            try:
                street_address = list(soup_location.find(
                    "span", {"itemprop": "streetAddress"}).stripped_strings)
                if "Suite" not in street_address[0]:
                    street_address = street_address[-1]
                else:
                    street_address = " ".join(street_address)
                #print(street_address)
            except:
                street_address = "<MISSING>"
            try:
                city = soup_location.find(
                    "span", {"itemprop": "addressLocality"}).text.strip()
            except:
                city = "<MISSING>"
            try:
                state = soup_location.find(
                    "span", {"itemprop": "addressRegion"}).text.strip()
            except:
                state = "<MISSING>"
            try:
                zipp = soup_location.find(
                    "span", {"itemprop": "postalCode"}).text.strip()
            except:
                zipp = "<MISSING>"
            try:
                phone = soup_location.find(
                    "span", {"itemprop": "telephone"}).text.replace("(main)", "").strip()
            except:
                phone = "<MISSING>"
            try:
                hours_of_operation = " ".join(list(soup_location.find(lambda tag: (
                    tag.name == "h4") and "Store Hours:"in tag.text.strip()).parent.stripped_strings)).replace("Store Hours:", "").strip()
            except:
                hours_of_operation = "<MISSING>"

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if store[2] in addresses:
                continue

            addresses.append(store[2])

            store = ["<MISSING>" if x == "" else x for x in store]

            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
