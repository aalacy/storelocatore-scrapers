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

    DOMAIN = "jomalone.ca"
    start_url = (
        "https://www.jomalone.ca/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents"
    )

    headers = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    formdata = "JSONRPC=%5B%7B%22method%22%3A%22locator.doorsandevents%22%2C%22id%22%3A4%2C%22params%22%3A%5B%7B%22fields%22%3A%22DOOR_ID%2C+DOORNAME%2C+EVENT_NAME%2C+EVENT_START_DATE%2C+EVENT_END_DATE%2C+EVENT_IMAGE%2C+EVENT_FEATURES%2C+EVENT_TIMES%2C+SERVICES%2C+STORE_HOURS%2C+ADDRESS%2C+ADDRESS2%2C+STATE_OR_PROVINCE%2C+CITY%2C+REGION%2C+COUNTRY%2C+ZIP_OR_POSTAL%2C+PHONE1%2C+LONGITUDE%2C+LATITUDE%22%2C%22radius%22%3A%2220000%22%2C%22latitude%22%3A51.04473309999999%2C%22longitude%22%3A-114.0718831%2C%22zip%22%3A%22%22%2C%22country%22%3A%22%22%2C%22state%22%3A%22Alberta%22%2C%22city%22%3A%22Calgary%22%2C%22region_id%22%3A%220%2C47%2C27%22%7D%5D%7D%5D"
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data[0]["result"]["value"]["results"].values():
        store_url = "<MISSING>"
        location_name = poi["DOORNAME"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["ADDRESS"]
        city = poi["CITY"]
        city = city if city else "<MISSING>"
        state = poi["STATE_OR_PROVINCE"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZIP_OR_POSTAL"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["COUNTRY"]
        country_code = country_code if country_code else "<MISSING>"
        if country_code not in ["United States", "UK", "Canada"]:
            continue
        store_number = poi["DOOR_ID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["PHONE1"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["LATITUDE"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["LONGITUDE"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["STORE_HOURS"]
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
