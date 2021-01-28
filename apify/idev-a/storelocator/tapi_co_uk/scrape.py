import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
import json

from util import Util  # noqa: I900

myutil = Util()


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
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.tapi.co.uk/stores/search"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select("div.stores-list.stores-list-all a")
    data = []
    for link in links:
        page_url = urljoin("https://www.tapi.co.uk/", link["href"])
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        scripts = soup1.find_all("script", type="application/ld+json")
        json_data = json.loads(scripts[0].contents[0])
        location_name = json_data["name"]
        street_address = json_data["address"]["streetAddress"]
        state = "<MISSING>"
        city = json_data["address"]["addressRegion"]
        zip = json_data["address"]["postalCode"]
        country_code = json_data["address"]["addressCountry"]
        store_number = json_data["branchCode"]
        phone = json_data["telephone"]
        location_type = json_data["@type"]
        hours_of_operation = "; ".join(json_data["openingHours"])

        json_data = json.loads(scripts[1].contents[0])
        latitude = json_data["geo"]["latitude"]
        longitude = json_data["geo"]["longitude"]
        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
