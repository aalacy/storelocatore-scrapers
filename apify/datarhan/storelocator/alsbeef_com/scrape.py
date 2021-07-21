import re
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

    start_url = "https://www.powr.io/wix/map/public.json?pageId=jew1u&compId=comp-kiap3wpb&viewerCompId=comp-kiap3wpb&siteRevision=257&viewMode=site&deviceType=desktop&locale=en&tz=America%2FChicago&regionalLanguage=en&width=882&height=587&instance=YhjSCE093S5bl2l9jxAdqjXzv87hduYb2M6CYz6s9Zc.eyJpbnN0YW5jZUlkIjoiNThkMjAxMzMtOGIxMi00NWZiLTgzNTMtYzQ3NDRkMThhNGI1IiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMjEtMDUtMDJUMTA6MjY6MjcuMzAzWiIsInZlbmRvclByb2R1Y3RJZCI6ImJ1c2luZXNzIiwiZGVtb01vZGUiOmZhbHNlLCJhaWQiOiI1MjRhNjJhYS1iOWMwLTRhOGItOGMxZC1mMzRkMWVlYTU4YTEiLCJzaXRlT3duZXJJZCI6ImJlZjNjMjYyLWY3Y2ItNDlmOC04NjExLWI5MGI0YTA3ZDdjMSJ9&currency=USD&currentCurrency=USD&commonConfig=%7B%22brand%22%3A%22wix%22%2C%22bsi%22%3A%22a1f5a05a-3d46-437d-ab8a-d79149828b2a%7C1%22%2C%22BSI%22%3A%22a1f5a05a-3d46-437d-ab8a-d79149828b2a%7C1%22%7D&vsi=719098ad-863b-40a2-a775-03c664859140&url=https://www.alsbeef.com/copy-of-about"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)

    all_locations = data["content"]["locations"]
    for poi in all_locations:
        store_url = "https://www.alsbeef.com/copy-of-about"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        if "COMING SOON" in location_name:
            continue
        raw_address = poi["address"].split(",")
        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[2].split()[0]
        zip_code = raw_address[2].split()[-1]
        country_code = raw_address[-1]
        store_number = "<MISSING>"
        phone = poi["number"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hours_of_operation = "<MISSING>"

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
