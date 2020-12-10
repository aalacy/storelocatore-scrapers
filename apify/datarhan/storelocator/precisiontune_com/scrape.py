import csv
import json
from lxml import etree

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

    DOMAIN = "precisiontune.com"
    start_url = "https://www.precisiontune.com/modules/location/ajax.aspx"

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    for state in states:
        formdata = {
            "StartIndex": "0",
            "EndIndex": "10000",
            "Longitude": "",
            "Latitude": "",
            "StateCode": state,
            "CountryCode": "US",
            "ZipCode": "",
            "City": "",
            "RangeInMiles": "50",
            "F": "GetNearestLocations",
        }
        response = session.post(start_url, data=formdata)
        data = json.loads(response.text)

        for poi in data["Locations"]:
            store_url = "https://www.precisiontune.com" + poi["CustomUrl"]
            location_name = poi["Name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["Address1"]
            if poi["Address2"]:
                street_address += ", " + poi["Address2"]
            street_address = street_address if street_address else "<MISSING>"

            check = "{} {}".format(location_name, street_address)
            if check in scraped_items:
                continue
            store_response = session.get(store_url)
            store_dom = etree.HTML(store_response.text)

            city = poi["City"]
            city = city if city else "<MISSING>"
            state = poi["State"]
            state = state if state else "<MISSING>"
            zip_code = poi["Zip"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["Country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = ""
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["Phone"]
            phone = phone if phone else "<MISSING>"
            location_type = ""
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["Latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["Longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = [
                elem.strip()
                for elem in store_dom.xpath('//div[@class="hours"]//text()')
                if elem.strip()
            ]
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

            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
