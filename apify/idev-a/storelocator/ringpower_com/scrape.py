import csv
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
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
    locator_domain = "https://www.ringpower.com"
    base_url = "https://www.ringpower.com/Umbraco/Api/locationsApi/GetLocations"
    r = session.get(base_url)
    items = json.loads(r.text)
    data = []
    for item in items:
        location_name = item["name"]
        street_address = myutil._valid(item["streetAddress"])
        city = myutil._valid(item["city"])
        state = myutil._valid(item["state"])
        zip = myutil._valid(item["zipCode"])
        country_code = "US"
        store_number = "<MISSING>"
        phone = myutil._valid(item.get("phone"))
        location_type = myutil._valid(item["speciality"])
        latitude = item["coordinate"]["lat"]
        longitude = item["coordinate"]["lng"]
        page_url = urljoin("https://www.ringpower.com", item["link"])
        r1 = session.get(page_url)
        hours_of_operation = "<MISSING>"
        soup1 = bs(r1.text, "lxml")
        label = soup1.select_one("li.location__detail.-hours label span")
        value = soup1.select_one("li.location__detail.-hours div.-block")
        if label and value:
            hours_of_operation = f"{label.text.strip()}: {value.text.strip()}"

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
        myutil._check_duplicate_by_loc(data, _item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
