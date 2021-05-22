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

    DOMAIN = "rdoequipment.com"
    start_url = "https://www.rdoequipment.com/rdo-api/branches/query"
    headers = {
        "content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }
    frm = '{"equipmentTypes":[],"pageNumber":"1","pageSize":"200","searchRadius":90000,"Latitude":40.75368539999999,"Longitude":-73.9991637}'
    response = session.post(start_url, headers=headers, data=frm)
    data = json.loads(response.text)

    for poi in data["Items"]:
        store_url = poi["Url"]
        store_url = store_url if store_url else '<MISSING>'
        location_name = poi["BranchName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]["Street"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["Address"]["City"]
        city = city if city else "<MISSING>"
        state = poi["Address"]["StateCode"]
        state = state if state else "<MISSING>"
        zip_code = poi["Address"]["Zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Address"]["CountryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["BranchId"]
        phone = json.loads(poi["PhoneNumbers"])[0]["value"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Address"]["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Address"]["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo_data = json.loads(poi["Hours"])
        hoo_data = hoo_data["hourTypes"][0]["schedule"]
        hoo = []
        days_dict = {
            1: "monday",
            2: "tuesday",
            3: "wednesday",
            4: "thursday",
            5: "friday",
            6: "saturday",
            7: "sunday",
        }
        for elem in hoo_data:
            day = days_dict[elem["weekday"]]
            opens = elem["from"]
            closes = elem["to"]
            hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
