import csv
from lxml import etree

from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt
from sglogging import sglog

session = SgRequests()

DOMAIN = "xfinity.com"
website = "https://www.xfinity.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
}


@retry(stop=stop_after_attempt(3))
def request_with_retries(url):
    return session.get(url, headers=headers, timeout=10)


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
    log.info("Started")
    items = []
    start_url = "https://www.xfinity.com/local/index.html"

    response = request_with_retries(start_url)
    dom = etree.HTML(response.text)
    all_locations = []
    all_directories = dom.xpath('//a[@data-ya-track="directory_links"]/@href')
    for url in all_directories:
        if len(url.split("/")) == 3:
            all_locations.append(url)
            continue
        dir_response = request_with_retries("https://www.xfinity.com/local/" + url)
        dir_dom = etree.HTML(dir_response.text)
        all_dir_urls = dir_dom.xpath('//a[@data-ya-track="directory_links"]/@href')
        for dir_url in all_dir_urls:
            if len(dir_url.split("/")) == 3:
                all_locations.append(dir_url)
                continue
            sub_dir_response = request_with_retries(
                "https://www.xfinity.com/local/" + dir_url
            )
            sub_dir_dom = etree.HTML(sub_dir_response.text)
            all_sub_urls = sub_dir_dom.xpath(
                '//a[@data-ya-track="directory_links"]/@href'
            )
            all_locations += sub_dir_dom.xpath(
                '//a[@data-ya-track="dir_viewdetails"]/@href'
            )
            for sub_url in all_sub_urls:
                all_locations.append(sub_url)

    for loc_url in list(set(all_locations)):
        store_url = "https://www.xfinity.com/local/" + loc_url.replace("../", "")
        log.info(f"Scraping : {store_url}")
        store_response = request_with_retries(store_url)
        store_dom = etree.HTML(store_response.text)

        location_name = store_dom.xpath('//meta[@itemprop="name"]/@content')
        location_name = location_name[0] if location_name else "<MISSING>"
        try:
            street_address = store_dom.xpath(
                '//span[@class="c-address-street-1"]/text()'
            )
            street_address = street_address[0]
        except Exception:
            log.info(f"Street address err: {street_address}")
            raise Exception("Please check street address issue")

        city = store_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = store_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = store_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        country_code = store_dom.xpath('//abbr[@itemprop="addressCountry"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = store_dom.xpath('//div[@id="StoreType"]/@data-type')
        location_type = location_type[0] if location_type else "<MISSING>"
        latitude = store_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = store_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = store_dom.xpath('//tr[@itemprop="openingHours"]/@content')
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
