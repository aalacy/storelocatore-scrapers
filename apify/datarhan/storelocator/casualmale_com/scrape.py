import csv
import json
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

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

    DOMAIN = "casualmale.com"
    start_url = "https://stores.dxl.com/search?q={}&r=200"

    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        max_radius_miles=49,
        max_search_results=None,
    )

    for code in all_codes:
        response = session.get(start_url.format(code), headers=headers)
        data = json.loads(response.text)

        for poi in data["response"]["entities"]:
            store_url = "https://stores.dxl.com/" + poi["url"]
            location_name = poi["profile"]["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["profile"]["address"]["line1"]
            if poi["profile"]["address"]["line2"]:
                street_address += ", " + poi["profile"]["address"]["line2"]
            if poi["profile"]["address"]["line3"]:
                street_address += ", " + poi["profile"]["address"]["line3"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["profile"]["address"]["city"]
            city = city if city else "<MISSING>"
            state = poi["profile"]["address"]["region"]
            state = state if state else "<MISSING>"
            zip_code = poi["profile"]["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["profile"]["address"]["countryCode"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = ""
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["profile"]["mainPhone"]["display"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["profile"]["c_pagesLocatorStoreType"]
            location_type = location_type[0] if location_type else "<MISSING>"
            latitude = ""
            longitude = ""
            if poi["profile"].get("geocodedCoordinate"):
                latitude = poi["profile"]["geocodedCoordinate"]["lat"]
                longitude = poi["profile"]["geocodedCoordinate"]["long"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []

            if poi["profile"].get("hours"):
                for elem in poi["profile"]["hours"]["normalHours"]:
                    day = elem["day"]
                    opens = str(elem["intervals"][0]["start"])
                    opens = opens[:-2] + ":" + opens[-2:]
                    closes = str(elem["intervals"][0]["end"])
                    closes = closes[:-2] + ":" + closes[-2:]
                    hours_of_operation.append("{} {} - {}".format(day, opens, closes))
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

            check = "{} {}".format(location_name, street_address)
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
