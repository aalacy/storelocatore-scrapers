import re
import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    start_url = "http://www.berryblendz.com/find-a-store.php"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath(
        '//a[contains(text(), "Find a Store")]/following-sibling::a/@href'
    )
    for url in all_states:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations = dom.xpath(
            '//div[@class="who-we-are-blk-txt"]/p[@style="margin-bottom: 10px;"]'
        )

        for poi_html in all_locations:
            store_url = poi_html.xpath(".//a/@href")
            store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
            if store_url != "<MISSING>":
                loc_response = session.get(store_url)
                loc_dom = etree.HTML(loc_response.text)
            raw_address = poi_html.xpath(".//text()")
            raw_address = [
                e.strip() for e in raw_address if e.strip() and "ph:" not in e.lower()
            ]
            addr = parse_address_intl(" ".join(raw_address))
            city = addr.city
            city = city if city else "<MISSING>"
            location_name = poi_html.xpath(".//b/text()")
            location_name = location_name[0] if location_name else city
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            street_address = street_address if street_address else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = addr.country
            country_code = country_code if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath(".//text()")
            phone = [e.strip() for e in phone if "Ph:" in e]
            phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hoo = []
            if store_url != "<MISSING>":
                hoo = loc_dom.xpath(
                    '//div[contains(text(), "Hours")]/following-sibling::div[1]//text()'
                )
                geo = (
                    loc_dom.xpath('//a[contains(@href, "/maps/")]/@href')[0]
                    .split("/@")[-1]
                    .split(",")[:2]
                )
                if len(geo) == 1:
                    geo = (
                        loc_dom.xpath("//iframe/@src")[0]
                        .split("1d30")[-1]
                        .split("!3d")[0]
                        .split("!2d")
                    )
                latitude = geo[0]
                longitude = geo[1]
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = (
                " ".join(hoo[:14]).split(" hours. ")[-1] if hoo else "<MISSING>"
            )

            if street_address.startswith(phone.split("-")[0]):
                street_address = " ".join(street_address.split()[1:])

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
