import re
import csv
import json
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

    DOMAIN = "metrodiner.com"
    start_url = "https://metrodiner.com/locations/"

    response = session.get(
        start_url,
    )
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "window.data =")]/text()')[0]
    data = re.findall("locations:(.+)}", data.replace("\t", "").replace("\n", ""))[0]
    data = json.loads(data)

    for poi in data:
        store_url = poi["link"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        raw_address = etree.HTML(poi["display_address"])
        raw_address = raw_address.xpath("//text()")
        if len(raw_address) == 3:
            raw_address = [", ".join(raw_address[:2]), raw_address[2]]
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        hoo = poi["hours"].split(";")[:-1]
        hoo = [elem[2:] for elem in hoo]
        hoo = [
            elem.replace(",", " - ").replace("00", ":00").replace(":000", "0:00")
            for elem in hoo
        ]
        hours_of_operation = list(map(lambda day, hour: day + " " + hour, days, hoo))
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
