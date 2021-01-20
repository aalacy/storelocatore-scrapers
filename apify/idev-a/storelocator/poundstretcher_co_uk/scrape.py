import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
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
    base_url = "https://www.poundstretcher.co.uk/find-a-store"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    scripts = [
        script.contents[0] for script in soup.find_all("script") if script.contents
    ]
    items = []
    for script in scripts:
        if "initial_locations:" in script:
            items = json.loads(
                script.split("initial_locations:")[1]
                .strip()
                .split("min_zoom: 10,")[0]
                .strip()[:-1]
            )
            break

    data = []
    for item in items:
        page_url = "http://www.poundstretcher.co.uk/" + item["website_url"]
        location_name = myutil._valid(item["title"])
        _address = myutil._strip_list(item["address_display"].split("\n"))
        if len(_address) == 1:
            _address = myutil._strip_list(item["address_display"].split(","))

        if _address[-1] == "UK":
            _address.pop()

        if _address[0] == location_name:
            _address = _address[1:]

        zip = _address[-1]
        if len(zip.split(",")) > 1:
            zip = zip.split(",")[1]
            _address.pop()
            _address.append(zip.split(",")[0])

        if len(zip.split(" ")) > 2:
            zip = " ".join(zip.split(" ")[1:])
            _address.pop()
            _address.append(zip.split(" ")[0])

        # missing city in address_display, location_name can be city
        city = location_name.split(" ")[0]
        street_address = " ".join(_address[:-1])
        if len(_address) > 2:
            city = _address[-2]
            street_address = " ".join(_address[:-2])
            if len(city.split("\\")) > 1:
                city = city.split("\\")[1]
                street_address += " " + city.split("\\")[0]

        state = "<MISSING>"
        country_code = myutil._valid(item["country"])
        store_number = myutil._valid(item["location_id"])
        phone = myutil._valid_uk(item.get("phone"))
        location_type = "<MISSING>"
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "html.parser")
        if soup1.select("div#store-address"):
            store = soup1.select("div#store-address")[-1]
            if store:
                _address = [_ for _ in store.stripped_strings]
                if _address[-1].replace(" ", "").isdigit():
                    _address = _address[:-1]
                if _address[0].strip() == "Address & Contact Details":
                    _address = _address[1:]
                if _address[-1] == "UK":
                    _address.pop()

                location_type = _address[0]

        latitude = myutil._valid(item["latitude"])
        longitude = myutil._valid(item["longitude"])
        soup2 = bs(item["notes"], "lxml")
        hours = []
        hours_of_operation = "<MISSING>"
        for _ in soup2.select("tr"):
            if _.text:
                hours.append(f"{_.th.text.strip()} {_.td.text.strip()}")

        if hours:
            hours_of_operation = myutil._valid("; ".join(hours))
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


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
