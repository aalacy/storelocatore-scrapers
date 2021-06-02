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

    start_url = "https://surgefun.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[@aria-current="page"]/following-sibling::ul/li/a/@href'
    )
    for store_number in range(1, 100):
        url = f"https://plondex.com/wp/jsonquery/loadloc/9/{store_number}"
        loc_response = session.get(url, headers=hdr)
        if loc_response.status_code != 200 or not loc_response.text:
            continue
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath('//div[@class="col-md-12 text-center"]/p/text()')
        city = raw_address[-1].split(", ")[0]
        store_url = "https://surgefun.com/locations/"
        state = raw_address[-1].split(", ")[-1].split()[0]
        location_name = f"{city.upper()}, {state.upper()}"
        location_name = location_name if location_name else "<MISSING>"
        street_address = raw_address[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath(
            '//h4[contains(text(), "Business Hours")]/following::text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
