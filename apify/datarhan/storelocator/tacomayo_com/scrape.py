import re
import csv
import demjson
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "tacomayo.com"
    start_url = "http://tacomayo.com/locations.aspx#.YAQPXZNKgWp"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = re.findall("locations =(.+?);", response.text.replace("\n", ""))[0]
    data = (
        data.replace("\r", "").replace("  ", " ").replace("  ", " ").replace("  ", " ")
    )
    data = re.findall(r's\d+?" :(.+?),* "s\d+?"', data)

    for elem in data:
        poi = demjson.decode(
            elem.replace("new google.maps.LatLng(", '"').replace("),", '",')
        )
        store_url = "<MISSING>"
        location_name = poi["name"]
        street_address = poi["address"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        types = {0: "Classic Menu", 1: "Fresh Mex"}
        location_type = types[poi["type"]]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        latitude = poi["point"].split(",")[0]
        longitude = poi["point"].split(",")[1]
        hours_of_operation = "<MISSING>"

        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
