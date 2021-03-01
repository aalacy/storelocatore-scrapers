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
    items = []
    scraped_items = []

    session = SgRequests()

    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    }

    DOMAIN = "superdry.com"
    start_url = "https://stores.superdry.com/search?q={}&qp={}&l=en"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN, SearchableCountries.USA],
        max_radius_miles=50,
    )
    for code in all_codes:
        response = session.get(start_url.format(code, code), headers=headers)
        data = json.loads(response.text)
        all_locations += data["response"]["entities"]

    for poi in all_locations:
        store_url = poi["profile"]["websiteUrl"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["profile"]["c_cHeroSectionStoreName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["profile"]["address"]["line1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["profile"]["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["profile"]["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["profile"]["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["profile"]["address"]["countryCode"]
        store_number = poi["profile"]["meta"]["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["profile"].get("mainPhone")
        if phone:
            phone = phone["number"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi["profile"].get("geocodedCoordinate"):
            latitude = poi["profile"]["geocodedCoordinate"]["lat"]
            longitude = poi["profile"]["geocodedCoordinate"]["long"]
        hoo = []
        for elem in poi["profile"]["hours"]["normalHours"]:
            day = elem["day"]
            if elem["isClosed"]:
                hoo.append(f"{day} closed")
            else:
                opens = str(elem["intervals"][0]["start"]).replace("00", ":00")
                closes = str(elem["intervals"][0]["end"]).replace("00", ":00")
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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
