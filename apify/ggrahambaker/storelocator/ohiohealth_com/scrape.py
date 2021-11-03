import csv
from sgrequests import SgRequests
import json


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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


def fetch_data():
    session = SgRequests()
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    locator_domain = "https://www.ohiohealth.com/"
    url = "https://www.ohiohealth.com/api/findalocation/get?locq=&lat=39.1031182&lng=-84.5120196&dist=1000&endPoint=%2Fapi%2Ffindalocation%2Fget"
    r = session.get(url, headers=HEADERS)

    locs = json.loads(r.text)["results"]
    for loc in locs:
        location_name = loc["Name"]
        street_address = loc["AddressLine1"]
        if (
            "AddressLine2" in loc
            and loc["AddressLine2"] is not None
            and len(loc["AddressLine2"]) > 0
        ):
            street_address = street_address + ", " + loc["AddressLine2"]

        city = loc["City"]
        state = loc["State"]
        zip_code = loc["ZipCode"]

        phone_number = loc["Phone"]
        if phone_number is None:
            phone_number = "<MISSING>"
        lat = loc["Latitude"]
        longit = loc["Longitude"]

        page_url = locator_domain + loc["Url"]

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        if loc["Specialties"] is not None:
            loc_type_list = []
            for typ in loc["Specialties"]:
                loc_type_list.append(typ["Text"])
            location_type = " | ".join(loc_type_list)
            location_name = "OhioHealth " + location_type
        else:
            location_name = "OhioHealth"

        hours = "<MISSING>"
        if loc["Hours"] is not None:
            hours = loc["Hours"].strip()

        if hours == "":
            hours = "<MISSING>"
        if phone_number == "":
            phone_number = "<MISSING>"

        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            page_url,
        ]

        yield store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
