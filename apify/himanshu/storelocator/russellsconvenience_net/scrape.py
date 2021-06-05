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

    start_url = "http://russellsconvenience.net/index.php/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(@href, "maps")]')[1:]
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath("text()")
        if not location_name:
            continue
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        if location_name == "View On Larger Map":
            continue

        raw_address = (
            poi_html.xpath("@href")[0]
            .split("place/")[-1]
            .split("/")[0]
            .replace("+", " ")
            .split(",")
        )
        if len(raw_address) == 4:
            raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0]
        street_address = street_address if street_address else "<MISSING>"
        city = raw_address[1]
        if street_address == "1670 Broadway  1670 Broadway":
            street_address = "1670 Broadway"
            city = "DENVER"
        state = raw_address[-1].split()[0]
        zip_code = raw_address[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        raw_data = dom.xpath(
            '//span[strong[strong[a[contains(text(), "{}")]]]]/following-sibling::*//text()'.format(
                location_name
            )
        )
        if not raw_data:
            raw_data = dom.xpath(
                '//span[strong[span[span[a[contains(text(), "{}")]]]]]//text()'.format(
                    location_name
                )
            )
        if not raw_data:
            raw_data = dom.xpath(
                '//span[strong[a[contains(text(), "{}")]]]/following-sibling::span//text()'.format(
                    location_name
                )
            )
        if not raw_data:
            raw_data = dom.xpath(
                '//strong[a[contains(text(), "{}")]]/following-sibling::span/text()'.format(
                    location_name
                )
            )
        if not raw_data:
            raw_data = dom.xpath(
                '//div[strong[a[contains(text(), "{}")]]]/following-sibling::div//text()'.format(
                    location_name
                )
            )
        if not raw_data:
            if location_name == "Russell's Xpress":
                raw_data = ["720-881-2191"]
        if not raw_data:
            raw_data = dom.xpath(
                '//strong[a[contains(text(), "{}")]]/following-sibling::span//text()'.format(
                    location_name
                )
            )
        if not raw_data:
            raw_data = dom.xpath(
                '//span[strong[a[contains(text(), "{}")]]]//text()'.format(
                    location_name
                )
            )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        phone = raw_data[-1]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = poi_html.xpath("@href")[0].split("/@")[-1].split(",")[:2]
        latitude = geo[0]
        longitude = geo[1]
        hoo = dom.xpath(
            '//td[div[p[span[strong[strong[a[contains(text(), "{}")]]]]]]]/following-sibling::td[1]//text()'.format(
                location_name
            )
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        if not hoo:
            hoo = dom.xpath(
                '//td[*[*[*[*[a[contains(text(), "{}")]]]]]]/following-sibling::td[1]//text()'.format(
                    location_name
                )
            )
            hoo = [e.strip() for e in hoo if e.strip()]
        if not hoo:
            hoo = dom.xpath(
                '//td[*[*[*[*[*[a[contains(text(), "{}")]]]]]]]/following-sibling::td[1]//text()'.format(
                    location_name
                )
            )
            hoo = [e.strip() for e in hoo if e.strip()]
        if not hoo:
            hoo = dom.xpath(
                '//td[*[*[*[a[contains(text(), "{}")]]]]]/following-sibling::td[1]//text()'.format(
                    location_name
                )
            )
            hoo = [e.strip() for e in hoo if e.strip()]
        if not hoo:
            hoo = dom.xpath(
                '//td[*[*[a[contains(text(), "{}")]]]]/following-sibling::td[1]//text()'.format(
                    location_name
                )
            )
            hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        if location_name == "Russell's Xpress":
            hours_of_operation = "temporarily closed due to Covid-19"

        if "Open" in phone:
            hours_of_operation = phone
            phone = "303.623.9300"

        if "3011" in street_address:
            location_name = "Fisher Building Russell's Fisher Pharmacy"

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
