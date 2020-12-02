import csv
import json
from w3lib.url import add_or_replace_parameter

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
    scraped_items = []

    DOMAIN = "katespade.com"
    start_url = "https://katespade.brickworksoftware.com/locations_search?hitsPerPage=6&page=1&getRankingInfo=true&facets[]=*&aroundRadius=all&filters=domain:katespade.brickworksoftware.com+AND+publishedAt%3C%3D1606914432365&esSearch=%7B%22page%22:1,%22storesPerPage%22:6,%22domain%22:%22katespade.brickworksoftware.com%22,%22locale%22:%22en_US%22,%22must%22:[%7B%22type%22:%22range%22,%22field%22:%22published_at%22,%22value%22:%7B%22lte%22:1606914432365%7D%7D],%22filters%22:[],%22aroundLatLngViaIP%22:true%7D&aroundLatLngViaIP=true"

    all_poi = []
    response = session.get(start_url)
    data = json.loads(response.text)
    all_poi += data["hits"]

    for i in range(2, data["nbPages"] + 1):
        page_response = session.get(add_or_replace_parameter(start_url, "page", str(i)))
        page_data = json.loads(page_response.text)
        all_poi += page_data["hits"]

    for poi in all_poi:
        store_url = "https://www.katespade.com/stores/s/" + poi["attributes"]["slug"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["attributes"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["attributes"]["address1"]
        if poi["attributes"]["address2"]:
            street_address += ", " + poi["attributes"]["address2"]
        if poi["attributes"]["address3"]:
            street_address += ", " + poi["attributes"]["address3"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["attributes"]["city"]
        city = city if city else "<MISSING>"
        state = poi["attributes"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["attributes"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["attributes"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = ""
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["attributes"]["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["attributes"]["type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["attributes"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["attributes"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["relationships"]["hours"]:
            day = elem["displayDay"]
            opens = elem["displayStartTime"]
            closes = elem["displayEndTime"]
            hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
        if street_address not in scraped_items:
            scraped_items.append(street_address)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
