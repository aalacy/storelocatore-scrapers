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
    scraped_items = []

    DOMAIN = "stiga.com"
    start_url = "https://www.stiga.com/uk/amlocator/index/combined/"

    formdata = {
        "attributes": "attribute_id%5B%5D=18&option%5B18%5D=&attribute_id%5B%5D=21&option%5B21%5D=&attribute_id%5B%5D=26&option%5B26%5D=",
        "lat": "51.5073509",
        "lng": "-0.1277583",
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-newrelic-id": "VQ4OV1VVCBABV1dTDwgAVFw=",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.post(start_url, json=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["items"]:
        url = [
            elem for elem in poi["attributes"] if elem["attribute_code"] == "url_key"
        ][0]["value"]
        store_url = "https://www.stiga.com/uk/storelocator/location/{}/".format(url)
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        city = poi["city"]
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        country_code = poi["country"]
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
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
