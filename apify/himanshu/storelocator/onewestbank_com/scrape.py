import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.onewestbank.com/assets/csv/branchlocations.csv"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    with open("out.csv", "w") as f:
        writer = csv.writer(f)
        for line in response.iter_lines():
            writer.writerow(line.decode("utf-8").split(","))

    all_locations = csv.DictReader(open("out.csv"))
    for poi in all_locations:
        store_url = "https://www.onewestbank.com/branch-locator"
        location_name = poi['"BranchName"'][1:-1]
        street_address = poi['"Street"'][1:-1]
        city = poi['"City"'][1:-1]
        state = poi['"State"'][1:-1]
        zip_code = poi['"Zipcode"'][1:-1]
        country_code = "<MISSING>"
        store_number = poi['"BranchID"'][1:-1]
        phone = poi['"Phone"'][1:-1]
        location_type = "<MISSING>"
        latitude = poi['"Xcoord"'][1:-1]
        longitude = poi['"Ycoord"'][1:-1]
        hours_of_operation = poi['"HoursBiz"'][1:-1]

        item = [
            domain,
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
