import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
import re

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


def _headers():
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
        "referer": "https://fitrepublic.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }


def fetch_data():
    base_url = "https://fitrepublic.com/find-a-club"
    r = session.get(base_url, headers=_headers())
    soup = bs(r.text, "lxml")
    links = soup.select("nav.folder-nav li.page-collection a")
    data = []
    for link in links[1:]:
        page_url = urljoin("https://fitrepublic.com", link["href"])
        r1 = session.get(page_url, headers=_headers())
        soup1 = bs(r1.text, "lxml")
        location_name = soup1.select("div.sqs-block-content h1")[0].text
        store_number = "<MISSING>"
        horizontal_rule = soup1.select("div.sqs-block-horizontalrule")[0]
        main_block = horizontal_rule.next_sibling.next_sibling
        phone_block = main_block.find("p", string=re.compile("\\d{3}-\\d{4}$"))
        phone = myutil._valid(phone_block.text)
        address = [_ for _ in phone_block.previous_sibling.stripped_strings]
        country_code = "US"
        street_address = myutil._valid(address[0])
        state = myutil._valid(address[1].split(",")[1].strip().split(" ")[0])
        city = myutil._valid(address[1].split(",")[0])
        zip = myutil._valid(address[1].split(",")[1].strip().split(" ")[1])
        location_type = "<MISSING>"
        latitude = "<INACCESSIBLE>"
        longitude = "<INACCESSIBLE>"
        hours_of_operation = "; ".join(
            [_ for _ in horizontal_rule.next_sibling.stripped_strings][1:]
        )

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

        data.append(_item)
    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
