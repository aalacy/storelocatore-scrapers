import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    r = session.get("https://www.fosteroil.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for location in soup.find_all("div", {"data-testid": "richTextElement"}):
        location_details = list(location.stripped_strings)
        if len(location_details) < 5:
            continue
        store = []
        store.append("https://www.fosteroil.com")
        store.append(location_details[0])
        store.append(location_details[1])
        store.append(location_details[2].split(",")[0])
        store_zip_split = re.findall("([0-9]{5})", location_details[2])
        if store_zip_split:
            store_zip = store_zip_split[0]
        else:
            store_zip = "<MISSING>"
        state_split = re.findall("([A-Z]{2})", location_details[2])
        if state_split:
            state = state_split[0]
        else:
            state = "<MISSING>"
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[3].replace("Ph: ", ""))
        store.append("<MISSING>")
        # There was 1 entry which did not have url on its name so i had to get it from a different part
        if location.find("a") is not None:
            geo_location = location.find("a")["href"]
            lat = geo_location.split("/@")[1].split(",")[0]
            lng = geo_location.split("/@")[1].split(",")[1]

        else:
            lat = "<MISSING>"
            lng = "<MISSING>"
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append("https://www.fosteroil.com/locations")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
