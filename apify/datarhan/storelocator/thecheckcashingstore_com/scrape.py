import csv
import xml.etree.ElementTree as ET

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

    DOMAIN = "thecheckcashingstore.com"
    start_url = "https://www.thecheckcashingstore.com/StoreDetails/GoogleAPIServiceCall"
    hdr = {"Content-Type": "application/json"}
    body = '{"lat":30.24,"lng":-81.39,"startRcdNum":"0","radius":"50000","StoreNum":"","searchText":"    32004   "}'
    response = session.post(start_url, headers=hdr, data=body)
    dom = ET.fromstring(response.text)
    all_locations = dom.findall("Store")

    for poi in all_locations:
        store_url = "<MISSING>"
        location_name = poi.find("BusinessName").text
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi.find("Address1").text
        if poi.find("Address2").text:
            street_address += ", " + poi.find("Address2").text
        street_address = street_address if street_address else "<MISSING>"
        city = poi.find("City").text
        city = city if city else "<MISSING>"
        state = poi.find("Province").text
        state = state if state else "<MISSING>"
        zip_code = poi.find("PostalCode").text
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi.find("Country").text
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi.find("StoreNum").text
        store_number = store_number if store_number else "<MISSING>"
        phone = poi.find("Phone").text
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi.find("Latitude").text
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi.find("Longitude").text
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi.find("StoreHours").text
        hours_of_operation = (
            hours_of_operation.replace(";", ",") if hours_of_operation else "<MISSING>"
        )
        store_url = "https://www.thecheckcashingstore.com/StoreDetails/StoreDetails?US/{}/{}/{}/{}/{}"
        store_url = store_url.format(
            state,
            city.replace(" ", "-"),
            street_address.replace(" ", "-"),
            zip_code,
            store_number,
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

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
