# coding=UTF-8

import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
    }

    location_url = "https://papa-murphys-order-online-locations.securebrygid.com/zgrid/themes/13097/portal/index.jsp"
    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for dt in soup.find_all("div", {"class": "restaurant"}):
        city = list(dt.stripped_strings)[2].split(",")[0]
        location_name = list(dt.stripped_strings)[0]

        state = list(dt.stripped_strings)[2].split(",")[1].strip().split()[0]
        zipp = " ".join(list(dt.stripped_strings)[2].split(",")[1].strip().split()[1:])
        street_address = list(dt.stripped_strings)[1]
        phone = list(dt.stripped_strings)[3]
        hours_of_operation = (
            " ".join(list(dt.stripped_strings)[5:])
            .replace("(587) 619-1172 Get Directions ", "")
            .split("Order")[0]
            .replace("*", "")
        )
        page_url = dt.find("a", {"class": "button portalbtn"})["href"]
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        log = soup1.find_all("iframe")[-1]["src"].split("!2d")[1].split("!3d")[0]
        lat = (
            soup1.find_all("iframe")[-1]["src"]
            .split("!2d")[1]
            .split("!3d")[1]
            .split("!")[0]
        )

        store = []
        store.append("http://papamurphys.ca/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("CA")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(log)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [x.strip() if type(x) == str else x for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
