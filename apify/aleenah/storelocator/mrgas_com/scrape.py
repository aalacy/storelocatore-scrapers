import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup


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


session = SgRequests()

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():

    all = []

    res = session.get("http://mrgas.com")

    soup = BeautifulSoup(res.text, "html.parser")

    stores = soup.find("section", {"id": "comp-keeh2c47"}).find_all(
        "div", {"class": "_2bafp"}
    )

    del stores[0]  # Location title
    for store in stores:
        ps = store.find_all("p")
        loc = ps[0].text.strip()

        addr = ps[1].text.strip().split(",")
        sz = addr[-1].strip().split(" ")
        zip = sz[1]
        state = sz[0]
        del addr[-1]
        city = addr[-1]
        del addr[-1]
        street = ", ".join(addr)
        phone = ps[2].text
        tim = ps[3].text
        if "#" in loc:
            id = loc.split("#")[-1]
        else:
            id = "<MISSING>"
        all.append(
            [
                "http://mrgas.com",
                loc,
                street,
                city,
                state,
                zip,
                "US",
                id,  # store #
                phone,  # phone
                "<MISSING>",  # type
                "<MISSING>",  # lat
                "<MISSING>",  # long
                tim.strip(),  # timing
                "<MISSING>",
            ]
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
