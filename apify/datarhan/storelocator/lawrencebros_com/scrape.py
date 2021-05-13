import re
import csv
import json
from requests_toolbelt import MultipartEncoder

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

    start_url = "https://lawrencebros.com/ajax/index.php"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    frm = {
        "method": "POST",
        "apiurl": "https://lawrencebros.rsaamerica.com/Services/SSWebRestApi.svc/GetclientStoresbyClientapp/1/''",
    }
    me = MultipartEncoder(fields=frm)
    me_boundary = me.boundary[2:]
    me_body = me.to_string()
    headers = {
        "Content-Type": "multipart/form-data; charset=utf-8; boundary=" + me_boundary
    }
    response = session.post(start_url, data=me_body, headers=headers)
    data = json.loads(response.text)

    all_locations = data["GetClientStores"]
    for poi in all_locations:
        store_url = "https://lawrencebros.com/contact"
        location_name = poi["ClientStoreName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["AddressLine1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["StateName"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["StoreNumber"]
        phone = poi["StorePhoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        longitude = poi["Longitude"]
        hours_of_operation = poi["StoreTimings"]

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
