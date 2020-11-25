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

    DOMAIN = "goldsgym.com"

    start_url = "https://www.goldsgym.com/api/gyms/locate?country={}"
    countries = ["US", "CA"]
    for country in countries:
        response = session.get(start_url.format(country))
        data = json.loads(response.text)

        for poi in data["gyms"]:
            store_url = poi["siteurl"]
            location_name = poi["gym_name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]
            if poi["address_2"]:
                street_address += " " + street_address
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["postal_code"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["id"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["gym_settings"]["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["gym_type"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []
            for day, hours in poi["gym_settings"]["business_hours_this_week"].items():
                open_h = hours["open"]["date"].split()[-1].split(".")[0]
                close_h = hours["close"]["date"].split()[-1].split(".")[0]
                hours_of_operation.append("{} {} - {}".format(day, open_h, close_h))
            hours_of_operation = (
                ", ".join(hours_of_operation).replace("00:00:00 - 00:00:00", "closed") if hours_of_operation else "<MISSING>"
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
