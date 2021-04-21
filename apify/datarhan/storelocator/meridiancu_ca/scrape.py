import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.meridiancu.ca/Meridian/WebService.asmx/GetLocations"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    response = session.post(start_url, headers=hdr, data="{}")
    data = json.loads(response.text)
    data = json.loads(data["d"])

    for poi in data:
        store_url = (
            "https://www.meridiancu.ca/Contact-Us/Branch-Details.aspx?id={}".format(
                poi["ItemID"]
            )
        )
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["Title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["Province"]
        state = state if state else "<MISSING>"
        zip_code = poi["Postal"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["ItemID"]
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        longitude = poi["Longitude"]
        hoo = []
        for k, v in poi.items():
            if "Hours" in k:
                day = k.replace("Hours", "")
                hoo.append(f"{day} {v}")
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
