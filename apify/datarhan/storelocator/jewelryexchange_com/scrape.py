import csv
from urllib.parse import urljoin
from lxml import etree

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
    items = []

    start_url = "https://www.jewelryexchange.com/Location/Index"
    domain = "jewelryexchange.com"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[span[contains(text(), "Map")]]/@ng-href')
    for url in all_locations:
        store_url = urljoin("https://www.jewelryexchange.com/", url)
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        raw_data = loc_dom.xpath(
            '//span[@ng-bind-html="StoreModel.StoreAddress"]/text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip()]

        location_name = loc_dom.xpath('//h2[@class="ng-binding"]/text()')[0].split(
            " - "
        )[0]
        street_address = raw_data[0]
        city = raw_data[1].split(", ")[0]
        if "Store Closed" in city:
            continue
        state = raw_data[1].split(", ")[-1].split()[0].replace(".", "")
        zip_code = raw_data[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@ng-if="isMobile == false"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath('//iframe[@class="MapContainer"]/@src')[0]
            .split("sll=")[-1]
            .split("&")[0]
            .split(",")
        )
        if len(geo) == 2:
            latitude = geo[0]
            longitude = geo[1]
        else:
            geo = (
                loc_dom.xpath('//iframe[@class="MapContainer"]/@src')[0]
                .split("!2d")[-1]
                .split("!2m")[0]
                .split("!3d")
            )
            latitude = geo[1]
            longitude = geo[0]
        hoo = loc_dom.xpath('//div[@ng-bind-html="StoreModel.StoreHours"]/text()')
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
