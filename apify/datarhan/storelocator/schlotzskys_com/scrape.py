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

    DOMAIN = "schlotzskys.com"

    all_codes = []
    us_codes = sgzip.for_radius(radius=50, country_code=SearchableCountries.USA)
    for code in us_codes:
        all_codes.append(code)

    start_url = "https://www.schlotzskys.com/sitecore/api/v0.1/storelocator/locations?locationname={}"
    headers = {
        "authority": "www.schlotzskys.com",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    }

    for code in all_codes:
        response = session.get(start_url.format(code), headers=headers)
        data = json.loads(response.text)

        for poi in data["Locations"]:
            store_url = "https://www.schlotzskys.com" + poi["Url"]
            location_name = poi["LocationName"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["StreetAddress"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["City"]
            city = city if city else "<MISSING>"
            state = poi["Region"]
            state = state if state else "<MISSING>"
            zip_code = poi["PostalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["CountryName"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["StoreNumber"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["Phone"]
            phone = phone if phone else "<MISSING>"
            location_type = ""
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["Latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["Longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []
            for elem in poi["Hours"]:
                if elem["FormattedDayOfWeek"] == "today":
                    continue
                day = elem["FormattedDayOfWeek"]
                opens = elem["Open"]
                close = elem["Close"]
                hours_of_operation.append("{} {} - {}".format(day, opens, close))
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
