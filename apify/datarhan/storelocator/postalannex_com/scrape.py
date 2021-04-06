import csv
from lxml import html
from urllib.parse import urljoin
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("postalannex_com")


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


headers = {
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}
session = SgRequests()


def fetch_data():
    # Your scraper here
    items = []
    DOMAIN = "postalannex.com"
    start_url = "https://www.postalannex.com/locations"
    r = session.get(start_url, headers=headers)
    dom = html.fromstring(r.text)
    all_locations = dom.xpath('//a[div[contains(text(), "Visit Website")]]/@href')
    logger.info("Number of Stores to be crawled: %s" % len(all_locations))

    for url in all_locations:
        store_url = urljoin(start_url, url)
        r_loc = session.get(store_url, headers=headers)
        loc_dom = html.fromstring(r_loc.text, "lxml")
        logger.info("Pulling the data from %s" % store_url)
        if loc_dom.xpath('//div[contains(text(), "Coming Soon")]'):
            continue
        location_name = loc_dom.xpath('//div[@id="views_title"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = " ".join(street_address) if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[1] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = store_url.split("/")[-1]
        phone = loc_dom.xpath('//a[@id="phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = loc_dom.xpath('//meta[@name="geo.position"]/@content')
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            geo = geo[0].split(";")
            latitude = geo[0]
            longitude = geo[1]
        hoo = loc_dom.xpath('//div[contains(@class, "store-hours")]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo[1:]) if hoo else "<MISSING>"

        item = [
            DOMAIN,
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
