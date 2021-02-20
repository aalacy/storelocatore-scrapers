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
    scraped_items = []

    DOMAIN = "chanel.com"
    start_url = "https://services.chanel.com/en_GB/storelocator/getStoreList"

    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    body = "division%5B%5D=1&productline%5B%5D=1&productline%5B%5D=2&productline%5B%5D=3&productline%5B%5D=4&division%5B%5D=2&productline%5B%5D=5&division%5B%5D=5&productline%5B%5D=18&productline%5B%5D=19&productline%5B%5D=25&division%5B%5D=3&productline%5B%5D=10&productline%5B%5D=14&productline%5B%5D=13&productline%5B%5D=12&geocodeResults=%5B%7B%22address_components%22%3A%5B%7B%22long_name%22%3A%22Manchester%22%2C%22short_name%22%3A%22Manchester%22%2C%22types%22%3A%5B%22locality%22%2C%22political%22%5D%7D%2C%7B%22long_name%22%3A%22Manchester%22%2C%22short_name%22%3A%22Manchester%22%2C%22types%22%3A%5B%22postal_town%22%5D%7D%2C%7B%22long_name%22%3A%22Greater+Manchester%22%2C%22short_name%22%3A%22Greater+Manchester%22%2C%22types%22%3A%5B%22administrative_area_level_2%22%2C%22political%22%5D%7D%2C%7B%22long_name%22%3A%22England%22%2C%22short_name%22%3A%22England%22%2C%22types%22%3A%5B%22administrative_area_level_1%22%2C%22political%22%5D%7D%2C%7B%22long_name%22%3A%22United+Kingdom%22%2C%22short_name%22%3A%22GB%22%2C%22types%22%3A%5B%22country%22%2C%22political%22%5D%7D%5D%2C%22formatted_address%22%3A%22Manchester%2C+UK%22%2C%22geometry%22%3A%7B%22bounds%22%3A%7B%22south%22%3A53.39990299999999%2C%22west%22%3A-2.3000969%2C%22north%22%3A53.5445879%2C%22east%22%3A-2.1468288%7D%2C%22location%22%3A%7B%22lat%22%3A53.4807593%2C%22lng%22%3A-2.2426305%7D%2C%22location_type%22%3A%22APPROXIMATE%22%2C%22viewport%22%3A%7B%22south%22%3A53.39990299999999%2C%22west%22%3A-2.3000969%2C%22north%22%3A53.5445879%2C%22east%22%3A-2.1468288%7D%7D%2C%22place_id%22%3A%22ChIJ2_UmUkxNekgRqmv-BDgUvtk%22%2C%22types%22%3A%5B%22locality%22%2C%22political%22%5D%7D%5D&radius=147.95"
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data["stores"]:
        store_url = "<MISSING>"
        location_name = poi["translations"][0]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["translations"][0]["address1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["translations"][0]["cityname"]
        city = city if city else "<MISSING>"
        state = poi["statename"]
        state = state if state else "<MISSING>"
        zip_code = poi["zipcode"]
        country_code = "<MISSING>"
        if poi["countryid"] == "77":
            country_code = "UK"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["translations"][0]["division_name"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"
        if poi["openinghours"]:
            day = poi["openinghours"][0]["day"]
            hours = poi["openinghours"][0]["opening"]
            hours_of_operation = f"{day} {hours}"

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
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
