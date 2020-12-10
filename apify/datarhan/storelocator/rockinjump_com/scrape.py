import csv
import json

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

    DOMAIN = "rockinjump.com"

    start_url = "https://rockinjump.com/wp-admin/admin-ajax.php"
    formdata = {
        "action": "get_stores",
        "lat": "39.8283",
        "lng": "-98.5795",
        "radius": "1420",
        "categories[0]": "",
    }
    headers = {
        "authority": "rockinjump.com",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://rockinjump.com",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    response = session.post(start_url, headers=headers, data=formdata)
    data = json.loads(response.text)

    for poi in data.values():
        store_url = poi["we"]
        location_name = poi["na"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["st"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["ct"]
        city = city if city else "<MISSING>"
        state = poi["rg"]
        state = state if state else "<MISSING>"
        zip_code = poi["zp"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["co"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["ID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["te"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = ""
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

        if state.isnumeric():
            new_state = zip_code
            zip_code = state
            state = new_state

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
