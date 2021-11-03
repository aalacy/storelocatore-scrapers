import csv
import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    base_url = "https://bergmanluggage.com"
    r = session.get(
        "https://bergmanluggage.com/pages/all-store-locations", headers=headers
    )
    soup = BeautifulSoup(r.text, "lxml")
    json_data = json.loads(
        soup.find("div", {"develic-map": re.compile("{")})["develic-map"]
    )["items"]

    zips = []

    for data in json_data:

        if "STORE IS CLOSED" in data["t"]:
            continue
        address = list(BeautifulSoup(data["b"], "lxml").stripped_strings)
        if "This Location Has Closed" in address:
            continue

        store = []
        store.append(base_url)
        store.append(data["t"])
        if "USA" in address[0]:
            store.append(" ".join(address[0].split(",")[0:-3]))
            store.append(address[0].split(",")[-3].strip())
            store.append(address[0].split(",")[-2].split(" ")[-2])
            zip_code = address[0].split(",")[-2].split(" ")[-1]
            store.append(zip_code)
        else:
            store.append(" ".join(address[0].split(",")[0:-2]))
            store.append(address[0].split(",")[-2].strip())
            store.append(address[0].split(",")[-1].split(" ")[-2])
            zip_code = address[0].split(",")[-1].split(" ")[-1]
            store.append(zip_code)

        zips.append(zip_code)
        store.append("US")
        store.append("<MISSING>")
        store.append(address[1] if len(address) == 2 else "<MISSING>")
        store.append("<MISSING>")
        store.append(data["lt"])
        store.append(data["lg"])
        store.append("<MISSING>")
        store.append("https://bergmanluggage.com/pages/all-store-locations")
        yield store

    text_url = "https://bergmanluggage.com/pages/all-store-locations-1"
    r = session.get(text_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    text_data = soup.table.find_all("td")

    for data in text_data:
        raw_data = list(data.stripped_strings)
        zip_code = raw_data[-2].split()[-1].strip()
        if zip_code not in zips:

            phone = (
                raw_data[-1]
                .replace("Phone:", "")
                .replace("Phone", "")
                .replace(":", "")
                .replace(" 1-", "")
                .replace("- (", "")
                .replace("(", "")
                .replace(") -", "-")
                .replace(")", "-")
            )
            phone = (re.sub(" +", "", phone)).strip()

            store = []
            store.append(base_url)
            store.append(raw_data[0])
            street_address = raw_data[-3]
            if "suite" in street_address.split()[0].lower():
                street_address = raw_data[-4].strip() + " " + street_address
            store.append(street_address)
            city_line = raw_data[-2].split()
            store.append(" ".join(city_line[:-2]).replace(",", "").strip())
            store.append(city_line[-2].strip())
            store.append(zip_code)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(text_url)
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
