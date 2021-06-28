import re
import csv
import demjson

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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    start_url = "https://www.barbour.com/storelocator"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    response = session.get(start_url)
    data = re.findall(r"amLocator\((.+?)\);", response.text.replace("\n", ""))[0]
    data = demjson.decode(data)

    for poi in data["jsonLocations"]["items"]:
        store_url = start_url
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        street_address = street_address.strip() if street_address else "<MISSING>"
        if street_address == "-":
            street_address = "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        if state.isdigit():
            state = "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        if country_code not in ["CA", "GB", "US"]:
            continue
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi["attributes"].get("stockist_type", {}).get("option_title"):
            location_type = poi["attributes"]["stockist_type"]["option_title"][0]
        latitude = poi["lat"]
        if latitude == "0.00000000":
            latitude = "<MISSING>"
        longitude = poi["lng"]
        if longitude == "0.00000000":
            longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        item = [
            domain,
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
