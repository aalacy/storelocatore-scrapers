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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "hardwarestore.com"
    start_url = "https://www.hardwarestore.com/storepickup/index/loadstore/"
    formdata = {
        "curPage": "1",
        "latitude": "",
        "longitude": "",
        "radius": "100",
        "nearby": "true",
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    response = session.post(start_url, json=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["storesjson"]:
        store_url = "https://www.hardwarestore.com/" + poi["rewrite_request_path"]
        location_name = poi["store_name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zipcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["storepickup_id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        hoo_dict = {}
        for key, value in poi.items():
            if key.endswith("_open"):
                day = key.split("_")[0]
                opens = value
                if hoo_dict.get(day):
                    hoo_dict[day]["opens"] = opens
                else:
                    hoo_dict[day] = {}
                    hoo_dict[day]["opens"] = opens
            if key.endswith("_close"):
                day = key.split("_")[0]
                closes = value
                if hoo_dict.get(day):
                    hoo_dict[day]["closes"] = closes
                else:
                    hoo_dict[day] = {}
                    hoo_dict[day]["closes"] = closes
        for day, hours in hoo_dict.items():
            hours_of_operation.append(f'{day} {hours["opens"]} - {hours["closes"]}')
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
