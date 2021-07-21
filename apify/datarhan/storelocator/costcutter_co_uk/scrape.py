import csv
import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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

    domain = "costcutter.co.uk"
    start_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=20&location={}&limit=25&api_key=c6803232fc9ac63c541dc43cd8434aca&v=20181201&resolvePlaceholders=true&languages=en_GB&entityTypes=location"

    all_coods = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        expected_search_radius_miles=20,
        max_search_results=None,
    )

    all_locations = []
    for code in all_coods:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        all_locations += data["response"]["entities"]

    for poi in all_locations:
        store_url = poi.get("landingPageUrl")
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["line1"]
        if poi["address"].get("line2"):
            street_address += " " + poi["address"]["line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["meta"]["id"]
        phone = poi.get("mainPhone")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi.get("geocodedCoordinate"):
            latitude = poi["geocodedCoordinate"]["latitude"]
            longitude = poi["geocodedCoordinate"]["longitude"]
        hoo = []
        if poi.get("hours"):
            for day, hours in poi["hours"].items():
                if day == "holidayHours":
                    continue
                if hours.get("openIntervals"):
                    opens = hours["openIntervals"][0]["start"]
                    closes = hours["openIntervals"][0]["end"]
                    hoo.append(f"{day} {opens} - {closes}")
                else:
                    hoo.append(f"{day} closed")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
