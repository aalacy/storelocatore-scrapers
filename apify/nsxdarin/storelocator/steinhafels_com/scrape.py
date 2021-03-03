import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("steinhafels_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://www.steinhafels.com/Location/GetLocationsJson"
    r = session.get(url, headers=headers)
    website = "steinhafels.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        name = item["StoreName"]
        loc = "https://www.steinhafels.com/location/details/" + item["UrlName"]
        add = item["Address"]
        city = item["City"]
        state = item["State"]
        zc = item["ZipCode"]
        phone = item["PhoneNumber"]
        store = item["StoreCode"]
        lat = item["Latitude"]
        lng = item["Longitude"]
        if "-mattress" in loc:
            name = name + " Mattress Store"
        if item["IsFurnitureStore"] is True:
            name = name + " Furniture Store"
        hours = item["SundayHours"]
        hours = hours + "; " + item["MondayHours"]
        hours = hours + "; " + item["TuesdayHours"]
        hours = hours + "; " + item["WednesdayHours"]
        hours = hours + "; " + item["ThursdayHours"]
        hours = hours + "; " + item["FridayHours"]
        hours = hours + "; " + item["SaturdayHours"]
        yield [
            website,
            loc,
            name,
            add,
            city,
            state,
            zc,
            country,
            store,
            phone,
            typ,
            lat,
            lng,
            hours,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
