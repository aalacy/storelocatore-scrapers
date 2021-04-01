import csv
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "alonbrands.com"
    start_url = "https://alonbrands.com/wp-admin/admin-ajax.php"
    hdr = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=100,
        max_search_results=None,
    )
    for lat, lng in all_coordinates:
        formdata = {
            "action": "csl_ajax_onload",
            "address": "",
            "formdata": "addressInput=",
            "lat": str(lat),
            "lng": str(lng),
            "options[distance_unit]": "miles",
            "options[dropdown_style]": "none",
            "options[ignore_radius]": "0",
            "options[immediately_show_locations]": "1",
            "options[initial_radius]": "100",
            "options[label_directions]": "Directions",
            "options[label_email]": "Email",
            "options[label_fax]": "Fax:+",
            "options[label_phone]": "Phone:+",
            "options[label_website]": "Website",
            "options[loading_indicator]": "",
            "options[map_center]": "United+States",
            "options[map_center_lat]": str(lat),
            "options[map_center_lng]": str(lng),
            "options[map_domain]": "maps.google.com",
            "options[map_end_icon]": "http://alonbrands.wpengine.com/wp-content/plugins/store-locator-le/images/icons/bulk_blue.png",
            "options[map_home_icon]": "http://alonbrands.wpengine.com/wp-content/plugins/store-locator-le/images/icons/box_yellow_home.png",
            "options[map_region]": "us",
            "options[map_type]": "roadmap",
            "options[no_autozoom]": "0",
            "options[use_sensor]": "false",
            "options[zoom_level]": "4",
            "options[zoom_tweak]": "1",
            "radius": "100",
        }

        response = session.post(start_url, headers=hdr, data=formdata)
        data = json.loads(response.text)
        all_locations += data["response"]

    for poi in all_locations:
        store_url = poi["sl_pages_url"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        street_address = (
            street_address.replace(" &amp;", "") if street_address else "<MISSING>"
        )
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["data"]["sl_id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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
