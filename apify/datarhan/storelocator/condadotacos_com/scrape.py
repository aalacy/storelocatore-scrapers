import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    start_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=500&location={}&limit=50&api_key=f758e5b45905bc090af86915406d345c&v=20181201&resolvePlaceholders=true&entityTypes=Restaurant&savedFilterIds=192172006"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=500
    )
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        data = json.loads(response.text)
        all_locations += data["response"]["entities"]

    for poi in all_locations:
        store_url = poi["landingPageUrl"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["line1"]
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["meta"]["id"]
        phone = poi["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["geocodedCoordinate"]["latitude"]
        longitude = poi["geocodedCoordinate"]["longitude"]
        hoo = []
        for day, hours in poi["hours"].items():
            opens = hours["openIntervals"][0]["start"]
            closes = hours["openIntervals"][0]["end"]
            hoo.append(f"{day} {opens} - {closes}")
        hoo = [e.strip() for e in hoo if e.strip()][1:]
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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
