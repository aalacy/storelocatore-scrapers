import re
import csv

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

    start_url = "https://mosersfoods.com/ajax/index.php"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "method": "POST",
        "apiurl": "https://mosersfoods.rsaamerica.com/Services/SSWebRestApi.svc/GetClientStores/1",
    }
    response = session.post(start_url, headers=hdr, data=frm).json()

    all_locations = response["GetClientStores"]
    for poi in all_locations:
        store_url = "https://mosersfoods.com/contact"
        location_name = poi["ClientStoreName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["AddressLine1"]
        city = poi["City"]
        state = poi["StateName"]
        zip_code = poi["ZipCode"]
        country_code = "<MISSING>"
        store_number = poi["StoreNumber"]
        phone = poi["StorePhoneNumber"]
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
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
