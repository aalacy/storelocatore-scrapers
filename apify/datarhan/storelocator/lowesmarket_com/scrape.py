import csv
import json

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "lowesmarket.com"
    start_url = "https://lowesmarket.com/wp-admin/admin-ajax.php"
    formdata = {
        "action": "csl_ajax_search",
        "address": "",
        "formdata": "addressInput=",
        "lat": "37.09024",
        "lng": "-95.712891",
        "options[distance_unit]": "miles",
        "options[dropdown_style]": "",
        "options[ignore_radius]": "0",
        "options[immediately_show_locations]": "0",
        "options[initial_radius]": "100",
        "options[label_directions]": "Directions",
        "options[label_email]": "Email",
        "options[label_fax]": "Fax: ",
        "options[label_phone]": "Phone: ",
        "options[label_website]": "View this store's weekly ad",
        "options[loading_indicator]": "",
        "options[map_center]": "United States",
        "options[map_center_lat]": "37.09024",
        "options[map_center_lng]": "-95.712891",
        "options[map_domain]": "maps.google.com",
        "options[map_end_icon]": "http://www.lowesmarket.com/wp-content/plugins/store-locator-le/images/icons/bulb_blue-dot.png",
        "options[map_home_icon]": "http://www.lowesmarket.com/wp-content/plugins/store-locator-le/images/icons/blank.png",
        "options[map_region]": "us",
        "options[map_type]": "roadmap",
        "options[no_autozoom]": "0",
        "options[use_sensor]": "false",
        "options[zoom_level]": "3",
        "options[zoom_tweak]": "1",
        "radius": "5000",
    }
    response = session.post(start_url, data=formdata)
    data = json.loads(response.text)

    for poi in data["response"]:
        store_url = poi["url"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["data"]["sl_store"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["data"]["sl_address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["data"]["sl_hours"]

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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
