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

    DOMAIN = "wafdbank.com"
    start_url = "https://www.wafdbank.com/locations"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    states_urls = dom.xpath(
        '//h2[contains(text(), "Browse Locations by State")]/following-sibling::p/a/@href'
    )
    for url in states_urls:
        state_response = session.get(
            "https://www.wafdbank.com/page-data/locations/{}/page-data.json".format(
                url.split("/")[-1]
            )
        )
        data = json.loads(state_response.text)
        for elem in data["result"]["pageContext"]["stateData"]["branch_locations"]:
            all_locations.append(elem["PageURL"])

    for url in list(set(all_locations)):
        store_url = "https://www.wafdbank.com" + url
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        store_data = store_dom.xpath('//script[@data-react-helmet="true"]/text()')
        poi = json.loads(store_data[0])
        location_name = poi["name"]
        if not location_name:
            continue
        location_name = (
            location_name.replace("&#x27;", "'").replace("&amp;", "")
            if location_name
            else "<MISSING>"
        )
        street_address = poi["address"]["streetAddress"]
        street_address = (
            street_address.replace("&quot;", "") if street_address else "<MISSING>"
        )
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["branchCode"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["_type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = ""
        longitude = ""
        if poi["geo"]:
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
        if "locations/washington" in store_url:
            latitude = "48.646755"
            longitude = "-118.737804"
        else:
            latitude = latitude if latitude else "<MISSING>"
            longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["openingHoursSpecification"]:
            day = elem["dayOfWeek"].split("/")[-1]
            opens = elem["opens"][:-3]
            closes = elem["closes"][:-3]
            hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = ", ".join(hours_of_operation)
        if "Saturday" not in hours_of_operation:
            hours_of_operation += ", Saturday Closed"
        if "Sunday" not in hours_of_operation:
            hours_of_operation += ", Sunday Closed"

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
