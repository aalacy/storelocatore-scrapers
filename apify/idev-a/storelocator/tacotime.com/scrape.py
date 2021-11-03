import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import re
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
    data = []

    locator_domain = "https://www.tacotime.com/"
    base_url = (
        "https://www.tacotime.com/locator/index.php?brand=7&mode=desktop&pagesize=5&q="
    )
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    all_scripts = " ".join(
        [_.contents[0] for _ in soup.select("script") if len(_.contents)]
    )
    scripts = re.findall(
        r'{"StoreId":\d{4},"Latitude":\d+.\d+,"Longitude":\-\d+.\d+', all_scripts
    )
    for script in scripts:
        script += "}"
        script = json.loads(script)
        page_url = urljoin(
            "https://www.tacotime.com",
            f"/stores/{script['StoreId']}",
        )
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        store_number = script["StoreId"]
        location_name = (
            myutil._valid(soup1.select_one("div.info h1").text)
            .replace(f"#{script['StoreId']}", "")
            .strip()
        )
        street_address = (
            soup1.select_one("li.address.icon-address").text.replace(",", "").strip()
        )
        address = [_.text for _ in soup1.select("li.address span")]
        city = address[0].replace(",", "").strip()
        state = address[1].strip()
        zip = address[2].strip()
        country_code = "US"
        phone = myutil._valid(soup1.select_one("li.phone.icon-phone a").text)
        location_type = "<MISSING>"
        latitude = script["Latitude"]
        longitude = script["Longitude"]
        hours_of_operation = myutil._valid(
            "; ".join([_.text for _ in soup1.select("div.hours ul li")])
        )

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


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
