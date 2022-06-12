import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    r = session.get("https://www.thegrill.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for location in soup.find_all(
        "div", {"class": re.compile("location_block wire_bknd")}
    ):
        if "Permanently Closed" in location.text:
            continue
        location_request = session.get(location.find("a")["href"], headers=headers)
        location_soup = BeautifulSoup(location_request.text, "lxml")
        name = location_soup.find("h1").text.strip()
        address = list(
            location_soup.find("div", {"class": "detail address"}).stripped_strings
        )
        hours = (
            " ".join(
                list(
                    location_soup.find(
                        "div", {"class": "detail store_hours"}
                    ).stripped_strings
                )
            )
            .replace("Hours", "")
            .strip()
        )
        store = []
        store.append("https://www.thegrill.com")
        store.append(name)
        store.append(address[0].split(",")[0])
        store.append(address[0].split(",")[1].strip())
        store.append(address[0].split(",")[2].split(" ")[-2])
        store.append(address[0].split(",")[2].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(address[1].replace("P: ", ""))
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours.replace("\xa0", " "))
        store.append(location.find("a")["href"])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
