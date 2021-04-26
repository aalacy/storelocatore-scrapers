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

    DOMAIN = "adecco.co.uk"
    start_url = "https://www.adecco.co.uk/globalweb/branch/branchsearch"

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    body = '{"dto":{"Latitude":"51.5073509","Longitude":"-0.1277583","MaxResults":"1000","Radius":"5000","Industry":"ALL","RadiusUnits":"MILES"}}'
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data["Items"]:
        store_url = "https://www.adeccousa.co.uk/" + poi["ItemUrl"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["BranchName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]
        if poi["AddressExtension"]:
            street_address += ", " + poi["AddressExtension"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["CountryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["BranchCode"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["PhoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["ScheduleList"]:
            day = elem["WeekdayId"]
            opens = elem["StartTime"].split("T")[-1]
            closes = elem["EndTime"].split("T")[-1]
            hours_of_operation.append("{} {} - {}".format(day, opens, closes))
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
