import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "sixt.co.uk"
    start_url = "https://www.sixt.co.uk/car-hire/united-kingdom/"

    all_locations = []
    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
    all_cities = dom.xpath('//div[@class="toplocation-item fade-bottom"]/img/@alt')
    for city in all_cities:
        response = session.get(
            f"https://web-api.orange.sixt.com/v1/locations?term={city}&vehicleType=car&type=station&profileId=&includeTypes=city"
        )
        data = json.loads(response.text)
        all_locations += data

    for poi in all_locations:
        if not poi.get("subtitle"):
            continue
        loc_response = session.get(
            "https://web-api.orange.sixt.com/v1/locations/{}".format(poi["id"])
        )
        data = json.loads(loc_response.text)

        store_url = "<MISSING>"
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        addr = parse_address_intl(poi["subtitle"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_2 + " " + addr.street_address_1
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        if country_code != "United Kingdom":
            continue
        store_number = poi["id"]
        phone = data["stationInformation"]["contact"]["telephone"]
        location_type = poi["type"]
        latitude = data["coordinates"]["latitude"]
        longitude = data["coordinates"]["longitude"]
        hoo = []
        for day, hours in data["stationInformation"]["openingHours"]["days"].items():
            if day == "holidays":
                continue
            if hours.get("openings"):
                opens = hours["openings"][0]["open"]
                closes = hours["openings"][0]["close"]
                hoo.append(f"{day} {opens} - {closes}")
            else:
                hoo.append(f"{day} closed")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
