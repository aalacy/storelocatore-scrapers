import re
import csv
from time import sleep
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgFirefox


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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.54thstreetgrill.com/54th-all-locations.html"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//h4[@class="local-name"]/a/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        with SgFirefox() as driver:
            driver.get(store_url)
            sleep(30)
            loc_dom = etree.HTML(driver.page_source)
            raw_address = loc_dom.xpath('//div[@id="locationContact"]/text()')
            raw_address = [e.strip() for e in raw_address if e.strip()]

            location_name = loc_dom.xpath("//h1/text()")[0]
            street_address = raw_address[0]
            city = " ".join(raw_address[1].split(", ")[0].split()[:-1])
            state = raw_address[1].split(", ")[0].split()[-1]
            state = state if state else "<MISSING>"
            zip_code = raw_address[1].split(", ")[-1]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = raw_address[-1]
            location_type = "<MISSING>"
            hoo = loc_dom.xpath('//p[strong[contains(text(), "SERVING FOOD")]]/text()')
            if not hoo:
                hoo = loc_dom.xpath(
                    '//h3[contains(text(), "Hours of Operation")]/following-sibling::p[1]/text()'
                )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = (
                " ".join(hoo).replace("*", "").replace(" Same hours as above", "")
                if hoo
                else "<MISSING>"
            )

            driver.switch_to.frame(driver.find_element_by_id("mapIndividual"))
            loc_dom = etree.HTML(driver.page_source)
            geo = (
                loc_dom.xpath('//a[contains(@href, "maps")]/@href')[-1]
                .split("@")[-1]
                .split(",")[:2]
            )
            latitude = geo[0]
            longitude = geo[1]

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
