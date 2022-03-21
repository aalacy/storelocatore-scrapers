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

    start_url = "https://www.fruitfulyield.com/stores/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//div[@class="stores-listing"]/a')
        for poi_html in all_locations:
            store_url = poi_html.xpath("@href")[0]
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

            location_name = poi_html.xpath('.//span[@class="store-name"]/text()')
            location_name = location_name[0] if location_name else "<MISSING>"
            street_address = poi_html.xpath('.//span[@class="street"]/text()')
            street_address = street_address[0] if street_address else "<MISSING>"
            city = poi_html.xpath('.//span[@class="city"]/text()')[0].split(", ")[0]
            state = (
                poi_html.xpath('.//span[@class="city"]/text()')[0]
                .split(", ")[-1]
                .split()[0]
            )
            zip_code = (
                poi_html.xpath('.//span[@class="city"]/text()')[0]
                .split(", ")[-1]
                .split()[-1]
            )
            country_code = re.findall('addressCountry":"(.+?)"', driver.page_source)
            country_code = country_code[0] if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath('.//span[@class="phone"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = re.findall('latitude":(.+?),', driver.page_source)[0]
            longitude = re.findall('longitude":(.+?)}', driver.page_source)[0]
            hoo = hoo = loc_dom.xpath('//div[@class="venue-hours"]//text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo[1:]) if hoo else "<MISSING>"

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
