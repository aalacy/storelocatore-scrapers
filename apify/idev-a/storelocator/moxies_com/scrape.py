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


def _parse_detail(locator_domain, links):
    data = []
    for link in links:
        page_url = urljoin("https://moxies.com", link["href"])
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        location_name = soup1.select_one("h1.title span").text.strip()
        contact_info = soup1.select("div.contact-info p a")
        street_address = soup1.select_one('div.adr div[itemprop="streetAddress"]').text
        city = soup1.select_one('div.adr span[itemprop="addressLocality"]').text
        state = soup1.select_one('div.adr span[itemprop="addressRegion"]').text
        zip = soup1.select_one('div.adr div[itemprop="postalCode"]').text
        country_code = myutil.get_country_by_code(state)
        phone = myutil._valid(contact_info[1].string)
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        direction = contact_info[0]["href"].split("/")[-1].strip().split(",")
        latitude = direction[0].strip()
        longitude = direction[1].strip()
        hours_of_operation = soup1.select_one("h2.subtitle").text
        if "closed" in hours_of_operation.lower():
            hours_of_operation = "Closed"
        else:
            tags = soup1.select("table.hours tr")
            hours = []
            for tag in tags:
                hours.append(
                    f"{tag.select_one('td.day').text.strip()} {tag.select_one('td.opening').text.strip()}-{tag.select_one('td.closing').text}"
                )
            hours_of_operation = myutil._valid("; ".join(hours))

        _item = [
            locator_domain,
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

        data.append(_item)

    return data


def fetch_data():

    data = []

    base_url = "https://moxies.com/location-finder?usredirect=no"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select(
        "ul.call-location-block__locations li.call-location-block__location > a"
    )
    data += _parse_detail("https://moxies.com/", links)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
