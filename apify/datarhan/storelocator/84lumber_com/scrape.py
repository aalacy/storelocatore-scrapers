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

    DOMAIN = "84lumber.com"
    start_url = "https://www.84lumber.com/umbraco/surface/StoreSupport/StoreSearch?radius=50000&storeId=null&latitude=40.189676&longitude=-80.134642"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(json.loads(response.text))

    for poi in data:
        store_url = (
            "https://www.84lumber.com/store-locator/store-detail?storeId={}".format(
                poi["StoreNumber"]
            )
        )
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["Zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["StoreNumber"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi["IsRetailStore"]:
            location_type = "RetailStore"
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        hoo = {}
        for day, hours in poi.items():
            if "OpenHours" in day:
                day = day.replace("OpenHours", "")
                if hoo.get(day):
                    hoo[day]["open"] = hours
                else:
                    hoo[day] = {}
                    hoo[day]["open"] = hours
            if "CloseHours" in day:
                day = day.replace("CloseHours", "")
                if hoo.get(day):
                    hoo[day]["close"] = hours
                else:
                    hoo[day] = {}
                    hoo[day]["close"] = hours
        for day, hours in hoo.items():
            opens = hours["open"]
            closes = hours["close"]
            hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            ", ".join(hours_of_operation).replace("12:00AM - 12:00AM", "Closed")
            if hours_of_operation
            else "<MISSING>"
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
