import csv
import json

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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "lepainquotidien.com"

    all_locations = []
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], max_radius_miles=100
    )
    for lat, lng in all_coords:
        start_url = (
            "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location="
            + f"{lat},{lng}"
            + "&radius=200&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false}}"
        )
        response = session.get(start_url)
        data = json.loads(response.text)
        all_locations += data["response"]["entities"]

    for poi in all_locations:
        location_name = poi.get("c_bIReference")
        if not location_name:
            location_name = poi["meta"]["id"].replace("-", " ")
        street_address = poi["address"]["line1"]
        store_url = poi["c_facebookWebsiteOverride"].split("?")[0]
        city = poi["address"]["city"]
        state = poi["address"].get("region")
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["countryCode"]
        if country_code != "GB":
            continue
        store_number = "<MISSING>"
        phone = poi["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = ", ".join(poi["meta"]["schemaTypes"])
        latitude = poi["geocodedCoordinate"]["latitude"]
        longitude = poi["geocodedCoordinate"]["longitude"]
        hoo = []
        for day, hours in poi["hours"].items():
            if hours.get("isClosed"):
                hoo.append(f"{day} closed")
            else:
                opens = hours["openIntervals"][0]["start"]
                closes = hours["openIntervals"][0]["end"]
                hoo.append(f"{day} {opens} - {closes}")
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
