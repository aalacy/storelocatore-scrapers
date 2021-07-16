import re
import csv
from lxml import etree
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
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://herefordhouse.com/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="entry-content"]/div/div[@class="wpb_column vc_column_container vc_col-sm-3"]'
    )
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//a/@href")[0]
        with SgFirefox() as driver:
            driver.get(store_url)
            driver.implicitly_wait(15)
            iframe = driver.find_element_by_xpath("//iframe[contains(@src, 'google')]")
            driver.switch_to.frame(iframe)
            loc_dom = etree.HTML(driver.page_source)
            driver.switch_to.default_content()
            zip_code = loc_dom.xpath('//div[@class="address"]/text()')[0].split()[-1]
            loc_dom = etree.HTML(driver.page_source)

        location_name = loc_dom.xpath('//h1[@id="page-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//p[@style="text-align: center;"]/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        street_address = raw_address[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//strong[contains(text(), "CALL NOW")]/text()')
        if not phone:
            phone = poi_html.xpath(".//strong/text()")
        phone = phone[0].split("NOW")[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!2m3")[0]
            .split("!3d")
        )
        latitude = geo[-1]
        longitude = geo[0]
        hoo = loc_dom.xpath(
            '//h4[contains(text(), "Dine-in Hours:")]/following-sibling::p//text()'
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
