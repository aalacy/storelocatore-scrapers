import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://ravecinemas.com"
    r = session.get(
        "https://ravecinemas.com/full-theatre-list", headers=headers, verify=False
    )
    soup = BeautifulSoup(r.text, "lxml")
    for location in soup.find("div", {"class": "columnList wide"}).find_all("a"):
        locationtype = location["href"].split("/")[-1].split("-")[0]
        if (
            "cinemark" in locationtype
            or "century" in locationtype
            or "tinseltown" in locationtype
        ):
            locationtype = locationtype
        else:
            locationtype = "ravecinema"
        location_request = session.get(
            base_url + location["href"], headers=headers, verify=False
        )
        location_soup = BeautifulSoup(location_request.text, "lxml")
        store_number = (
            str(location_soup).split("var currentTheaterId =")[1].split(";")[0].strip()
        )
        if location_soup.find("div", {"class": "theatre-status-label"}):
            label = location_soup.find(
                "div", {"class": "theatre-status-label"}
            ).text.strip()
            if "Permanently Closed" in label or "closed" in label.lower():
                continue
        if location_soup.find("div", {"class": "theatreMap"}) is None:
            continue
        geo_location = location_soup.find("div", {"class": "theatreMap"}).find("img")[
            "data-src"
        ]
        location_details = json.loads(
            location_soup.find("script", {"type": "application/ld+json"}).text
        )
        address = location_details["address"][0]
        store = []
        store.append("https://ravecinemas.com")
        store.append(location_details["name"])
        if "NOW CLOSED".lower() in store[-1].lower():
            continue
        store.append(address["streetAddress"].replace("Located at", "").strip())
        store.append(address["addressLocality"])
        store.append(address["addressRegion"])
        store.append(address["postalCode"])
        store.append(address["addressCountry"])
        store.append(store_number)
        store.append(
            location_details["telephone"]
            if location_details["telephone"]
            else "<MISSING>"
        )
        store.append(locationtype)
        store.append(
            geo_location.split("&pp=")[1].split(",")[0]
            if geo_location.split("&pp=")[1].split(",")[0]
            else "<MISSING>"
        )
        store.append(
            geo_location.split("&pp=")[1].split(",")[1].split("&")[0]
            if geo_location.split("&pp=")[1].split(",")[1].split("&")[0]
            else "<MISSING>"
        )
        store.append("<MISSING>")
        store.append(base_url + location["href"])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
