import csv
import json
import sgzip
from sgzip import SearchableCountries

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

    DOMAIN = "alfaromeousa.com"

    all_codes = []
    us_zips = sgzip.for_radius(radius=200, country_code=SearchableCountries.USA)
    for zip_code in us_zips:
        all_codes.append(zip_code)

    start_url = "https://www.alfaromeousa.com/bdlws/MDLSDealerLocator?brandCode=Y&func=SALES&radius=200&resultsPage=1&resultsPerPage=100&zipCode={}"
    for code in all_codes:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        if not data.get("dealer"):
            continue

        for poi in data["dealer"]:
            store_url = poi["website"]
            store_url = store_url if store_url else "<MISSING>"
            location_name = poi["dealerName"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["dealerAddress1"]
            if poi["dealerAddress2"]:
                street_address += " " + poi["dealerAddress2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["dealerCity"]
            city = city if city else "<MISSING>"
            state = poi["dealerState"]
            state = state if state else "<MISSING>"
            zip_code = poi["dealerZipCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["dealerShowroomCountry"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["dealerCode"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["phoneNumber"]
            phone = phone if phone else "<MISSING>"
            location_type = ""
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["dealerShowroomLatitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["dealerShowroomLongitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []
            for day, hours in poi["departments"]["sales"]["hours"].items():
                hours_of_operation.append(
                    "{} {} - {}".format(
                        day, hours["open"]["time"], hours["close"]["time"]
                    )
                )
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

            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
