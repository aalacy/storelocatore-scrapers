import csv
import json
from urllib.parse import urljoin

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

    DOMAIN = "superdrug.com"
    start_url = "https://www.superdrug.com/getstorelocatoraddress.json"
    with open("gb.csv", newline="") as f:
        reader = csv.reader(f)
        cities = list(reader)

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-newrelic-id": "UwcAWVJVGwYEUVhTAQM=",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.get("https://www.superdrug.com/ajaxCSRFToken", headers=headers)
    token = response.text

    all_locations = []
    for city in cities:
        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-csrf-token": token,
        }
        formdata = {"q": city[0], "country": "GB", "services": ""}

        response = session.post(start_url, data=formdata, headers=headers)
        data = json.loads(response.text)
        all_locations += data["results"]

    for poi in all_locations:
        store_url = urljoin(start_url, poi["url"])
        location_name = poi["name"]
        street_address = poi["address"]["streetNumber"]
        city = poi["address"]["town"]
        state = poi["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["country"]["isocode"]
        store_number = poi["code"]
        location_type = "<MISSING>"
        phone = poi["address"]["phone"]
        latitude = poi["geoPoint"]["latitude"]
        longitude = poi["geoPoint"]["longitude"]
        hours_of_operation = []
        for elem in poi["openingHours"]["weekDayOpeningList"]:
            day = elem["weekDay"]
            opens = elem["openingTime"]["formattedHour"]
            closes = elem["closingTime"]["formattedHour"]
            hours_of_operation.append(f"{day} {opens} - {closes}")
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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
