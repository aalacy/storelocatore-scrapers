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

    DOMAIN = "tedbaker.com"
    start_url = "https://www.tedbaker.com/uk/json/stores/for-country?isocode=GB"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["data"]:
        store_url = "https://www.tedbaker.com/uk/store/{}".format(poi["name"])
        location_name = poi["displayName"]
        street_address = poi["address"]["line1"]
        if poi["address"].get("line2"):
            street_address += ", " + poi["address"]["line2"]
        city = poi["address"].get("town")
        if not city:
            city = poi["address"].get("line3")
        if not city:
            if ", " in street_address:
                city = street_address.split(", ")[-1]
                street_address = street_address.split(", ")[0]
        city = city if city else "<MISSING>"
        city = city.split(",")[0]
        state = "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["country"]["isocode"]
        store_number = poi["name"]
        location_type = poi["storeType"]["name"]
        phone = poi["address"].get("phone")
        phone = phone if phone else "<MISSING>"
        latitude = poi["geoPoint"]["latitude"]
        longitude = poi["geoPoint"]["longitude"]
        hours_of_operation = []
        if poi.get("openingHours"):
            for elem in poi["openingHours"]["weekDayOpeningList"]:
                if not elem.get("openingTime"):
                    continue
                day = elem["weekDay"]
                opens = elem["openingTime"]["formattedHour"]
                closes = elem["closingTime"]["formattedHour"]
                if not elem["closed"]:
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
