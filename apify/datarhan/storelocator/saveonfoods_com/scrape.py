import re
import csv
import json

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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "saveonfoods.com"
    start_urls = [
        "https://shop.saveonfoods.com/api/stores/v7/chains/8E4E398/stores?skip=0&take=999&region=AB",
        "https://shop.saveonfoods.com/api/stores/v7/chains/8E4E398/stores?skip=0&take=999&region=BC",
        "https://shop.saveonfoods.com/api/stores/v7/chains/8E4E398/stores?skip=0&take=999&region=MB",
        "https://shop.saveonfoods.com/api/stores/v7/chains/8E4E398/stores?skip=0&take=999&region=SK",
        "https://shop.saveonfoods.com/api/stores/v7/chains/8E4E398/stores?skip=0&take=999&region=YT",
    ]

    all_locations = []
    for url in start_urls:
        response = session.get(url)
        data = re.findall('({"Stores".+})', response.text)[0]
        data = json.loads(data)
        all_locations += data["Stores"]

    for poi in all_locations:
        store_url = "https://shop.saveonfoods.com/store/" + poi["PseudoStoreId"]
        location_name = poi["Retailer"]["DisplayName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Sections"][0]["Address"]["AddressLine1"]
        if poi["Sections"][0]["Address"]["AddressLine2"]:
            street_address += ", " + poi["Sections"][0]["Address"]["AddressLine2"]
        if poi["Sections"][0]["Address"]["AddressLine3"]:
            street_address += ", " + poi["Sections"][0]["Address"]["AddressLine3"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["Sections"][0]["Address"]["City"]
        city = city if city else "<MISSING>"
        state = poi["Sections"][0]["Address"]["Region"]
        state = state if state else "<MISSING>"
        zip_code = poi["Sections"][0]["Address"]["PostalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Sections"][0]["Address"]["CountryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["Retailer"]["StoreGroupId"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Sections"][0]["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["Sections"][0]["Section"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Sections"][0]["Coordinates"]["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Sections"][0]["Coordinates"]["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["Sections"][0]["SectionSchedule"]
        hours_of_operation = (
            hours_of_operation[0] if hours_of_operation else "<MISSING>"
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
