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
        city = poi.find("City")
        city = city.text if city else "<MISSING>"
        state = poi.find("Province")
        state = state.text if state else "<MISSING>"
        zip_code = poi.find("PostalCode")
        zip_code = zip_code.text if zip_code else "<MISSING>"
        country_code = poi.find("Country")
        country_code = country_code.text if country_code else "<MISSING>"
        store_number = poi.find("StoreNum")
        store_number = store_number.text if store_number else "<MISSING>"
        phone = poi.find("Phone")
        phone = phone.text if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi.find("Latitude")
        latitude = latitude.text if latitude else "<MISSING>"
        longitude = poi.find("Longitude")
        longitude = longitude.text if longitude else "<MISSING>"
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
