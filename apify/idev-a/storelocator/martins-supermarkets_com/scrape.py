import csv
from sgrequests import SgRequests
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


def _phone(phone):
    if phone:
        return phone.split("\n")[0].strip().replace("Phone:", "")
    else:
        return "<MISSING>"


def fetch_data():
    data = []

    locator_domain = "https://www.martinsgroceriestogo.com/"
    base_url = "https://api.freshop.com/1/stores?app_key=martins&has_address=true&limit=-1&token=a37ebe52509f935976c8ed2d68cbf25d"
    rr = session.get(base_url)
    locations = json.loads(rr.text)["items"]
    for location in locations:
        try:
            page_url = myutil._valid(location.get("url"))
            store_number = location["store_number"].strip()
            location_name = myutil._valid(location["name"])
            country_code = location.get("country", "US")
            street_address = "<MISSING>"
            if "address_1" in location:
                street_address = location.get("address_1")
            elif "address_0" in location:
                street_address = location.get("address_0")

            city = location["city"]
            state = location["state"]
            zip = location["postal_code"]
            phone = _phone(location["phone"])
            if phone == "<MISSING>":
                phone = _phone(location["phone_md"])
            location_type = "<MISSING>"
            latitude = location["latitude"]
            longitude = location["longitude"]
            hours_of_operation = myutil._valid(location.get("hours"))

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
        except Exception as err:
            print(err)
            import pdb

            pdb.set_trace()

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
