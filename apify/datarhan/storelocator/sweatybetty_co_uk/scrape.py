import csv
from lxml import etree
from urllib.parse import urljoin

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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "sweatybetty.com"
    start_url = "https://www.sweatybetty.com/shop-finder"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//div[@class="stores-accordion show-for-medium"]/div/div[1]//a[@class="store-link"]/@href'
    )
    all_locations += dom.xpath(
        '//div[@class="stores-accordion show-for-medium"]/div/div[2]//a[@class="store-link"]/@href'
    )

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//div[@class="store-details-header"]//h1/text()'
        )[0]
        raw_address = loc_dom.xpath(
            '//div[@class="small-6 medium-3 large-3 columns main-details"]/text()'
        )
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = raw_address[0]
        city = raw_address[1]
        city = city.split(",")[0] if city else "<MISSING>"
        if len(raw_address[1].split(",")) == 2:
            state = raw_address[1].split(",")[-1].strip()
        state = "<MISSING>"
        zip_code = raw_address[2]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "UK"
        store_number = store_url.split("=")[-1]
        location_type = "<MISSING>"
        phone = raw_address[-1]
        latitude = loc_dom.xpath("//div/@data-lat")[0]
        longitude = loc_dom.xpath("//div/@data-lng")[0]
        hoo = []
        for h_html in loc_dom.xpath("//div[@data-day]"):
            day = h_html.xpath(".//b/text()")[0].replace(":", "")
            opens = h_html.xpath(".//@data-open")[0]
            closes = h_html.xpath(".//@data-close")[0]
            hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
