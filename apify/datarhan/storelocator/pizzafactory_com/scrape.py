import csv
import json

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    items = []

    session = SgRequests()

    DOMAIN = "pizzafactory.com"
    start_url = "https://data.api.powerchord.com/forte/locator/5c36116a9710500007b99d7e"

    body = '{"radius":80000,"countToReturn":300,"latitude":34.0692042,"longitude":-118.4066574,"onLocator":true,"showLocationAssignments":true,"isTerritorySearch":false,"searchText":"90210"}'
    headers = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "authorization": "Panda eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJjIjoiIiwiZCI6MzE1MzYwMDAwLCJkaWQiOiIiLCJoIjoibG9jYXRpb25zLnBpenphZmFjdG9yeS5jb20iLCJpIjoxNjA5MTU3MjYyLCJvIjoiNWMzNjExNmE5NzEwNTAwMDA3Yjk5ZDdlIiwicyI6ImJjOGNiNjg4LWIyMTEtNDUzYi1hNjY2LWYxMjUxN2I1YWFkOCIsInQiOiI1YzM2MTE2YTk3MTA1MDAwMDdiOTlkN2UifQ.DACslw-YavCDQYrWDsjO4q_z2g3iHKY3oGboneAOrHpWv05l6-B8iL0HiTxLjCeMx0OhYfcSUIAuoYd3-iWf_g",
    }
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://{}.pizzafactory.com/".format(poi["subdomain"])
        location_name = poi["name"]
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["locationExternalID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day, hours in poi["hours"].items():
            if hours:
                opens = hours[0]["open"]
                closes = hours[0]["close"]
                hours_of_operation.append(f"{day} {opens} - {closes}")
            else:
                hours_of_operation.append(f"{day} closed")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            location_name,
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
