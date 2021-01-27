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

    DOMAIN = "clevelandclinic.org"
    start_url = "https://nli34ig0x3-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%3B%20JS%20Helper%20(2.28.0)&x-algolia-application-id=NLI34IG0X3&x-algolia-api-key=a134144c18c63ca12a4a12bcfb2ad7d7"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
    }
    body = '{"requests":[{"indexName":"locations_prod","params":"query=&hitsPerPage=1000&maxValuesPerFacet=500&page=0&getRankingInfo=true&facets=%5B%22types%22%2C%22specialties%22%2C%22services%22%2C%22searchCollections%22%5D&tagFilters="}]}'

    response = session.post(start_url, headers=headers, data=body)
    data = json.loads(response.text)

    for poi in data["results"][0]["hits"]:
        store_url = "https://my.clevelandclinic.org/locations/directions/{}-{}".format(
            poi["Id"], poi["bizId"]
        )
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["streetAddress1"]
        if poi["streetAddress2"]:
            street_address += ", " + poi["streetAddress2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["addressRegion"]
        if "United Arab Emirates" in state:
            continue
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["Id"]
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["types"]
        location_type = ", ".join(location_type) if location_type else "<MISSING>"
        latitude = poi["_geoloc"]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["_geoloc"]["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        if poi["operationDetails"]:
            if poi["operationDetails"][0]["openingHours"][0]["alwaysOpen"]:
                hours_of_operation = "24/7"
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

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
