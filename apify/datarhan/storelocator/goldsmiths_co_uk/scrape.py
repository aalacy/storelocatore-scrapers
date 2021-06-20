import json
import csv
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


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
    scraped_urls = []

    DOMAIN = "goldsmiths.co.uk"
    start_url = "https://www.goldsmiths.co.uk/store-finder?q=london&latitude={}&longitude={}&brand=StoreBV-Goldsmiths"

    all_locations = []
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=50,
        max_search_results=None,
    )
    for lat, lng in all_coords:
        data = session.get(start_url.format(lat, lng))
        try:
            data = json.loads(data.text)
        except Exception:
            continue
        all_locations += data["results"]

    for poi in all_locations:
        store_url = urljoin("https://www.goldsmiths.co.uk/", poi["url"])
        location_name = poi["displayName"]
        street_address = poi["address"]["line1"]
        if poi["address"]["line2"]:
            street_address += " " + poi["address"]["line2"]
        city = poi["address"]["town"]
        state = poi["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["country"]["isocode"]
        store_number = poi["name"]
        phone = poi["address"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["geoPoint"]["latitude"]
        longitude = poi["geoPoint"]["longitude"]
        hoo = []
        for e in poi["openingHours"]["weekDayOpeningList"]:
            day = e["weekDay"]
            if e.get("closed"):
                hoo.append(f"{day} closed")
            else:
                opens = e["openingTime"]["formattedHour"]
                closes = e["closingTime"]["formattedHour"]
                hoo.append(f"{day} {opens} - {closes}")
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
        if store_number not in scraped_urls:
            scraped_urls.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
