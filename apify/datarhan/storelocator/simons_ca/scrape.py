import re
import csv
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

    start_url = "https://www.simons.ca/en/stores--a13090"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//div[@itemprop="location"]/a/@href')
        for store_url in all_locations:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

            location_name = " ".join(
                [
                    e.capitalize()
                    for e in store_url.split("/")[-1].split("--")[0].split("-")
                ]
            )
            location_name = location_name if location_name else "<MISSING>"
            raw_address = loc_dom.xpath('//span[@itemprop="address"]/text()')
            street_address = raw_address[0].strip()
            city = raw_address[-1].split(", ")[0].strip()
            state = raw_address[-1].split(", ")[-1].split()[0].strip()
            zip_code = " ".join(raw_address[-1].split(", ")[-1].split()[1:]).strip()
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
            phone = phone[0].strip() if phone else "<MISSING>"
            location_type = "<MISSING>"
            geo = (
                loc_dom.xpath('//a[@itemprop="hasMap"]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            latitude = geo[0]
            longitude = geo[1]
            hoo = loc_dom.xpath('//div[@class="simonsStore-regularHours"]//text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            if not hoo:
                location_type = "temporarily closed"
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
