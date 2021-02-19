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


def fetch_data():
    data = []

    locator_domain = "https://www.benefitcosmetics.com/"
    base_url = "https://api.benefitcosmetics.com/us/en/rest/storelocator/stores/?callback=jQuery21307271565409387377_1612435828814&1612435889926&key=952e29aebf5cec744b2097e69fdfb2f3999d8d1c&lat=51.5073509&lng=-0.1277583&radius=50000&unit=km&language=en-GB&programId=&nbp=true&_=1612435828817"
    rr = session.get(base_url)
    locations = json.loads(
        rr.text.replace("jQuery21307271565409387377_1612435828814(", "")[:-2]
    )["results"]["stores"]
    for location in locations:
        page_url = "<MISSING>"
        store_number = "<MISSING>"
        location_name = location["name"]
        country_code = myutil._valid(location.get("country", ""))
        street_address = (
            myutil._valid1(location["address_1"])
            + myutil._valid1(location["address_2"])
            + myutil._valid1(location["address_3"])
        )
        if not street_address.strip() or country_code not in [
            "United States",
            "UK",
            "Canada",
        ]:
            continue
        city = myutil._valid(location["city"])
        state = myutil._valid(location["state"])
        zip = myutil._valid(location["postal_code"])
        phone = myutil._valid(location["phone"])
        location_type = myutil._valid(location["store_type"])
        latitude = location["lat"]
        longitude = location["lng"]
        hours_of_operation = "<MISSING>"
        if location["mon_hrs_o"] and location["mon_hrs_c"]:
            hours_of_operation = ""
            hours_of_operation += (
                f'Mon:{location["mon_hrs_o"]}-{location["mon_hrs_c"]}; '
            )
            hours_of_operation += (
                f'Tue:{location["tue_hrs_o"]}-{location["tue_hrs_c"]}; '
            )
            hours_of_operation += (
                f'Tue:{location["wed_hrs_o"]}-{location["wed_hrs_c"]}; '
            )
            hours_of_operation += (
                f'Tue:{location["wed_hrs_o"]}-{location["wed_hrs_c"]}; '
            )
            hours_of_operation += (
                f'Tue:{location["thu_hrs_o"]}-{location["thu_hrs_c"]}; '
            )
            hours_of_operation += (
                f'Tue:{location["fri_hrs_o"]}-{location["fri_hrs_c"]}; '
            )
            hours_of_operation += (
                f'Tue:{location["sat_hrs_o"]}-{location["sat_hrs_c"]}; '
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

        myutil._check_duplicate_by_loc(data, _item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
