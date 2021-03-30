import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

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


def _parse_detail(links):
    data = []
    for link in links:
        base_url = "https://www.harvester.co.uk/restaurants"
        page_url = link["href"]
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        location_name = link.text.strip()
        location_type = "closed"
        hours_of_operation = "closed"
        country_code = "UK"
        store_number = "<MISSING>"
        if "CLOSED" in soup1.select_one("div.heading.parbase h1").text:
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zip = "<MISSING>"
            phone = "<MISSING>"
            location_type = "closed"
            hours_of_operation = "closed"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        else:
            street_address = soup1.select_one("div.premise--details .address span").text
            city = (
                soup1.select_one("div.premise--details .address span.city")
                .text.replace(",", "")
                .strip()
            )
            state = "<MISSING>"
            zip = soup1.select_one(
                "div.premise--details .address span.postcode"
            ).text.strip()
            phone = soup1.select_one(
                "div.premise--details .address span#header-phone-number"
            ).text.strip()
            location_type = "<MISSING>"
            loc = soup1.select_one("a[href*='maps']")["href"]
            latitude = loc.split("daddr=")[1].split(",")[0]
            longitude = loc.split("daddr=")[1].split(",")[1]
            lis = soup1.select("div.opening-times ul li")
            hours = []
            for li in lis:
                hours.append(
                    f'{li.select_one("span.day-of-week").text.strip()} {li.select_one("span.time-description").text.strip()}'
                )

            hours_of_operation = "; ".join(hours)

        _item = [
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
        myutil._check_duplicate_by_loc(data, _item)

    return data


def fetch_data():
    base_url = "https://www.harvester.co.uk/restaurants"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    sections = soup.select("div.accordion--accordion section")
    data = []
    for section in sections:
        _contents = section.select("div.accordion--content div.parbase")
        if len(_contents) > 1:
            # detail
            detail = (
                "https://www.harvester.co.uk/" + _contents[0].select_one("a")["href"]
            )
            r1 = session.get(detail)
            soup1 = bs(r1.text, "lxml")
            links = soup1.select("div.heading-with-link.parbase.section a")
            data += _parse_detail(links)
        else:
            data += _parse_detail(_contents[0].select("a"))

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
