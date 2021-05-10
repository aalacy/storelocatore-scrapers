import re
import csv
from lxml import etree

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

    start_url = "https://lavelierstores.com/store-finder-2/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//tr[td[@data-label="Address"]]')
    for poi_html in all_locations:
        country_code = "<MISSING>"
        store_url = start_url
        location_name = "<MISSING>"
        street_address = poi_html.xpath('.//td[@data-label="Address"]/p/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//td[@data-label="City/State"]/p/text()')
        if not city:
            city = poi_html.xpath('.//td[@data-label="City/Province"]/p/text()')
        exclude = False
        for ex in ["Mexico", "Taiwan", "Uruguay"]:
            if ex in city[0]:
                exclude = True
        if exclude:
            continue
        city = city[0].split(",")[0]
        state = poi_html.xpath('.//td[@data-label="City/State"]/p/text()')
        if not state:
            state = poi_html.xpath('.//td[@data-label="City/Province"]/p/text()')
        state = state[0].split(",")[-1].split()[0]
        zip_code = poi_html.xpath('.//td[@data-label="City/State"]/p/text()')
        country_code = "USA"
        if not zip_code:
            zip_code = poi_html.xpath('.//td[@data-label="City/Province"]/p/text()')
            country_code = "CA"
            state = "ON"
        zip_code = zip_code[0].split(",")[-1].split()[-1]
        map_url = poi_html.xpath(".//a/@href")[0]
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "/@" in map_url:
            geo = map_url.split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        hours_of_operation = "<MISSING>"

        if "Canada" in state:
            state = "<MISSING>"
        if "Canada" in zip_code:
            zip_code = "<MISSING>"
        if "Cookstown" in city:
            zip_code = "L0L 1L0"

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
