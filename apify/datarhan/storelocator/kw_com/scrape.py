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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "kw.com"
    start_url = "https://api-endpoint.cons-prod-us-central1.kw.com/graphql"

    headers = {"x-shared-secret": "MjFydHQ0dndjM3ZAI0ZHQCQkI0BHIyM="}
    query = """{
        ListOfficeQuery {
            id
            name
            address
            subAddress
            phone
            fax
            lat
            lng
            url
            contacts {
            name
            email
            phone
            __typename
            }
            __typename
        }
        }
    """
    payload = {"operationName": None, "variables": {}, "query": query}
    response = session.post(start_url, headers=headers, json=payload)
    all_poi = response.json()
    all_poi = all_poi["data"]["ListOfficeQuery"]

    for poi in all_poi:
        store_url = poi["url"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zip_code = "<MISSING>"
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["__typename"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
