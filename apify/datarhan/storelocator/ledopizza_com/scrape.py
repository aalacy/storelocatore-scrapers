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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "ledopizza.com"
    start_url = "https://order.ledopizza.com/api/vendors/regions?excludeCities=true"
    headers = {
        "__requestverificationtoken": "",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "x-olo-request": "1",
        "x-olo-viewport": "Desktop",
        "x-requested-with": "XMLHttpRequest",
    }

    all_locations = []
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for state in data:
        url = "https://order.ledopizza.com/api/vendors/search/{}".format(state["code"])
        response = session.get(url, headers=headers)
        data = json.loads(response.text)
        all_locations += data["vendor-search-results"]

    for poi in all_locations:
        store_url = "<MISSING>"
        location_name = poi["name"]
        street_address = poi["streetAddress"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi.get("country")
        country_code = country_code if country_code else "<MISSING>"
        location_type = "<MISSING>"
        store_number = poi["id"]
        phone = poi["phoneNumber"]
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hours_of_operation = []
        for elem in poi["weeklySchedule"]["calendars"][0]["schedule"]:
            day = elem["weekDay"]
            hours = elem["description"]
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
