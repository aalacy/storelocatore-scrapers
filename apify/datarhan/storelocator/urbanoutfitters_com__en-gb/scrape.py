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

    DOMAIN = "urbanoutfitters.com"
    start_url = "https://www.urbanoutfitters.com/api/misl/v1/stores/search?brandId=51%7C01&distance=25&urbn_key=937e0cfc7d4749d6bb1ad0ac64fce4d5"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data["results"]:
        if poi["country"] != "UK":
            continue
        store_url = "<MISSING>"
        if poi.get("slug"):
            store_url = "https://www.urbanoutfitters.com/en-gb/stores/{}".format(
                poi["slug"]
            )
        location_name = poi["addresses"]["marketing"]["name"].split(" - ")[0]
        city = poi["addresses"]["marketing"]["city"]
        street_address = poi["addresses"]["marketing"]["addressLineOne"]
        state = poi["addresses"]["marketing"]["state"]
        zip_code = poi["addresses"]["marketing"]["zip"]
        country_code = poi["addresses"]["iso2"]["country"]
        location_type = poi.get("storeType")
        location_type = location_type if location_type else "<MISSING>"
        store_number = poi["number"]
        phone = poi["addresses"]["marketing"].get("phoneNumber")
        phone = phone if phone else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi.get("loc"):
            latitude = poi["loc"][1]
            longitude = poi["loc"][0]

        days_dict = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wendsday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Satarday",
            "7": "Sunday",
        }
        hours_of_operation = []
        for day_id, hours in poi["hours"].items():
            day = days_dict[day_id]
            opens = hours["open"]
            closes = hours["close"]
            if hours["open"] != "Closed":
                hours_of_operation.append(f"{day} {opens} - {closes}")
            else:
                hours_of_operation.append(f"{day} Closed")
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
