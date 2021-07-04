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

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//div[@data-widget_type="heading.default"]/div[1]/h2[@class="elementor-heading-title elementor-size-default"]/text()'
    )
    all_locations = list(set(all_locations))
    all_locations = [e.lower() for e in all_locations if len(e.split(", ")) == 2]

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
        if location_name == "WINSTON SALEM, NC":
            location_name = "WINSTON-SALEM, NC"
        if location_name == "MONROE, LA":
            continue
        if location_name == "HOPE MILLS, NC":
            location_name = "Fayetteville, NC".upper()
        if location_name == "MARY ESTHER, FL":
            location_name = "Ft. Walton, FL".upper()
        if location_name == "EDMOND, OK":
            location_name = "Oklahoma City, OK".upper()
        street_address = raw_address[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        if street_address == "2723 W. Pinhook Rd":
            continue
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

        if location_name.lower() not in all_locations:
            continue

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
