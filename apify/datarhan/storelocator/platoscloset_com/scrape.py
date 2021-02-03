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
    session = SgRequests()

    items = []

    hdr = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3IiOiJhbm9uLXRlbXBsYXRlLXVzZXIiLCJjaWQiOiI3YzRhMjJjOC0yNjk1LTQyMDMtOTI2Zi02NGRmM2M2NjY0MjQiLCJvcmRlcmlkIjoiMG9qdkZNUDVoVUNEbXJqRGVrSGNvQSIsInUiOiIyOTgzMzEwIiwidXNydHlwZSI6ImJ1eWVyIiwicm9sZSI6WyJNZUFkZHJlc3NBZG1pbiIsIk1lQWRtaW4iLCJNZUNyZWRpdENhcmRBZG1pbiIsIk1lWHBBZG1pbiIsIlNob3BwZXIiLCJTdXBwbGllclJlYWRlciIsIlN1cHBsaWVyQWRkcmVzc1JlYWRlciIsIlBhc3N3b3JkUmVzZXQiLCJCdXllclJlYWRlciIsIkRvY3VtZW50UmVhZGVyIl0sIm5iZiI6MTYxMjM0MjcxNCwiZXhwIjoxNjEyOTQ4MTE0LCJpYXQiOjE2MTIzNDMzMTQsImlzcyI6Imh0dHBzOi8vYXV0aC5vcmRlcmNsb3VkLmlvIiwiYXVkIjoiaHR0cHM6Ly9hcGkub3JkZXJjbG91ZC5pbyJ9.GWu5FzlXZWEuPh5bbXpZqGz1OrH34npcvCOZ4dHS_v4",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    }

    DOMAIN = "platoscloset.com"
    start_url = "https://api.ordercloud.io/v1/suppliers?pageSize=20&page=1&Active=true&xp.isCoop=false&sortBy=Name"
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)

    for poi in data["Items"]:
        hoo_url = "https://api.ordercloud.io/v1/suppliers/{}/addresses/{}".format(
            poi["ID"], poi["ID"]
        )
        hoo_response = session.get(hoo_url, headers=hdr)
        data = json.loads(hoo_response.text)

        store_url = "https://www.platoscloset.com/locations/{}".format(
            poi["xp"]["slug"]
        )
        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["Street1"]
        city = data["City"]
        state = data["State"]
        zip_code = data["Zip"]
        country_code = data["Country"]
        store_number = data["ID"]
        phone = data["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["xp"]["latitude"]
        longitude = poi["xp"]["longitude"]
        hoo = data["xp"]["hours"]
        hours_of_operation = []
        for day, hours in hoo.items():
            hours_of_operation.append(f"{day} {hours}")
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
