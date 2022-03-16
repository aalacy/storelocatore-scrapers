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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    addresses = []
    base_url = "https://www.graduatehotels.com/"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = ""

    r = session.get("https://www.graduatehotels.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for li in soup.find("ul", {"class": "directory-navigation"}).find_all(
        "a", {"class": "location-item"}
    ):
        page_url = li["href"]
        r_loc = session.get(page_url, headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, "lxml")
        try:
            address = list(
                soup_loc.find("div", class_="footer-address")
                .find("address")
                .stripped_strings
            )
            street_address = address[0].strip()
            openings = soup_loc.find("p", class_="lead banner-copy")[
                "data-main-subtitle"
            ]
            if "Opening Summer 2021" in openings:
                location_type = "Coming Soon"
            elif "Opening Spring 2021" in openings:
                location_type = "Coming Soon"
            else:
                location_type = "Graduate Hotel"
            city = address[1].split(",")[0].strip()
            state = address[1].split(",")[1].split()[0].strip()
            zipp = address[1].split(",")[1].split()[-1].strip()
            location_name = city
            phone_tag = " ".join(
                list(soup_loc.find("div", class_="footer-contact").stripped_strings)
            )
            phone_list = re.findall(
                re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag)
            )
            if phone_list:
                phone = phone_list[0].strip()
            else:
                phone = "<MISSING>"
            coord = (
                soup_loc.find("div", class_="footer-address")
                .find("address")
                .find("a", class_="map-link")["href"]
            )
            r_c = session.get(coord, headers=headers)
            soup_c = BeautifulSoup(r_c.text, "lxml")
            latitude = (
                soup_c.find_all("meta")[-7]["content"]
                .split("markers=")[1]
                .split("%2C")[0]
                .strip()
            )
            longitude = (
                soup_c.find_all("meta")[-7]["content"]
                .split("markers=")[1]
                .split("%2C")[1]
                .split("&")[0]
                .strip()
            )
        except:
            pass

        if "View Tucson on" in city:
            city = "Tucson"
            location_name = city
            street_address = "930 E 2nd St"
            state = "AZ"
            zipp = "<MISSING>"
            phone = "520 467 5900"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        if "View East Lansing on" in city:
            city = "East Lansing"
            location_name = city
            street_address = "130 W. Grand River Avenue"
            state = "MI"
            zipp = "48823"
            phone = "517 348 0900"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        if "New York" in location_name:
            location_name = "Roosevelt Island"

        store = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
            page_url,
        ]
        store = ["<MISSING>" if x == "" else x for x in store]
        store = [
            str(x).encode("ascii", "ignore").decode("ascii").strip()
            if x
            else "<MISSING>"
            for x in store
        ]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
