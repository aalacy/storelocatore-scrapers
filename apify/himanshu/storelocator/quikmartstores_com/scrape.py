import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

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
    addressess = []

    base_url = "http://www.quikmartstores.com/store-locations/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    for i in soup.find("section", {"class": "content-section"}).find_all(
        "div", {"class": "col"}
    ):

        page_url = i.find("a", {"class": "thickbox"})["href"]

        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        addr = list(soup1.find("div", {"id": "popup-details"}).stripped_strings)
        name = addr[0]
        street_address = addr[1].split(",")[0]
        city = addr[1].split(",")[1].strip()
        state = addr[1].split(",")[2].strip().split(" ")[0]
        zip = addr[1].split(",")[2].strip().split(" ")[1]
        phone = addr[2]
        map_link = soup1.find("a")["href"]
        coords = session.get(map_link).url
        if "/@" in coords:
            lat = coords.split("/@")[1].split(",")[0]
            lng = coords.split("/@")[1].split(",")[1]
        else:
            soup = BeautifulSoup(session.get(map_link).text, "lxml")
            file_name = open("data.txt", "w", encoding="utf-8")
            file_name.write(str(soup))
            try:
                map_href = soup.find(
                    "a", {"href": re.compile("https://maps.google.com/maps?")}
                )["href"]
                lat = (
                    str(BeautifulSoup(session.get(map_href).text, "lxml"))
                    .split("/@")[1]
                    .split(",")[0]
                )
                lng = (
                    str(BeautifulSoup(session.get(map_href).text, "lxml"))
                    .split("/@")[1]
                    .split(",")[1]
                )
            except:
                lat = str(soup).split("/@")[1].split(",")[0]
                lng = str(soup).split("/@")[1].split(",")[1]

        store = []
        store.append(base_url)
        store.append(name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url if page_url else "<MISSING>")

        if store[2] in addressess:
            continue
        addressess.append(store[2])

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
