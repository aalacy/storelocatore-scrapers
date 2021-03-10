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
    locator_domain = "https://banking.cit.com/find-bank-location"
    base_url = "https://banking.cit.com/ajax/get-location-data?branch=true"
    r = session.get(base_url)
    locations = json.loads(r.text)["locations"]
    data = []
    for location in locations:
        page_url = "<MISSING>"
        location_name = location["name"]
        country_code = "US"
        zip = location["zip"]
        city = location["city"]
        state = location["state"]
        street_address = myutil._valid(
            location["address"] + " " + myutil._valid1(location.get("address_two"))
        )
        phone = location["phone"]
        store_number = "<MISSING>"
        location_type = location["type"][0]
        latitude = location["lat"]
        longitude = location["long"]
        soup = bs(location["hours"], "lxml")
        hours = [_.text for _ in soup.select(".ls-hours") if _.text]
        _hours = []
        for hour in hours:
            if hour == "Lobby Hours:":
                continue
            if hour == "Drive-up Hours:":
                break
            _hours.append(hour.replace("–", "-"))

        hours_of_operation = "; ".join(_hours)
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
