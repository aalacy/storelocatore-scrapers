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
    scraped_items = []

    DOMAIN = "remax.com"
    start_url = (
        "https://public-api-gateway-prod.kube.remax.booj.io/personnel/office/list/"
    )

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "timeout": "10000",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
    }
    body = '{"offset":0,"count":24,"include":["offices"],"filters":{"officeStatus":"OPEN","officeClass":"OFFICE","countryCode":"USA"},"sorts":[],"custom":{"filters":{}},"options":{}}'
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)
    all_locations = data["data"]["offices"]["results"]

    for i in range(24, data["data"]["offices"]["total"] + 24, 24):
        body = (
            '{"offset":%s,"count":24,"include":["offices"],"filters":{"officeStatus":"OPEN","officeClass":"OFFICE","countryCode":"USA"},"sorts":[],"custom":{"filters":{}},"options":{}}'
            % i
        )
        response = session.post(start_url, data=body, headers=headers)
        data = json.loads(response.text)
        all_locations += data["data"]["offices"]["results"]

    for poi in all_locations:
        location_name = poi["officeName"]
        store_number = poi["masterCustomerId"]
        store_url = "https://www.remax.com/real-estate-offices/remax-{}/{}"
        store_url = store_url.format(
            location_name.replace("RE/MAX ", "").replace(" ", "-"), store_number
        )
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address1"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postalCode"]
        country_code = poi["countryCode"]
        phone = poi["phones"]
        phone = phone[0]["phoneNumber"] if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi["mlsIdxData"]:
            location_type = poi["mlsIdxData"][0]["relatedEntityType"]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi["officeGeoLocation"]:
            latitude = poi["officeGeoLocation"][0]["geoPoint"]["lat"]
            longitude = poi["officeGeoLocation"][0]["geoPoint"]["lon"]
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
