import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin

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
    base_url = "https://www.citymd.com/all-locations"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select("div.question-list a.link-btn")
    data = []
    for link in links:
        page_url = urljoin("https://www.citymd.com", link["href"])
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        location_name = soup1.h1.string
        address = [sibling.string for sibling in soup1.h1.next_siblings][1]
        street_address, city, state, zip, country_code = myutil.parse_address_simple(
            address
        )
        phone = soup1.select_one("a.location-phone-number").string
        store_number = link["href"].split("/")[-1]
        location_type = soup1.select_one("h6.text-upper").text
        direction = (
            soup1.select_one("a.directions-link")["href"].split("/")[-2].split(",")
        )
        latitude = direction[0]
        longitude = direction[1]
        tags = soup1.select_one("h4.margin-bottom-0").find_all_next("p")
        hours_of_operation = "; ".join(
            [tag.text for tag in tags if tag.select_one("span.dow")]
        )

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
