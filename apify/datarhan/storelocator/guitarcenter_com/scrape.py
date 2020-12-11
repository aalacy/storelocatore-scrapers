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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "guitarcenter.com"
    start_url = "https://stores.guitarcenter.com/index.html"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations_urls = []
    directories_urls = dom.xpath('//a[@class="Directory-listLink"]/@href')
    for url in directories_urls:
        if not url.endswith(".html"):
            all_locations_urls.append(url)
        else:
            full_subdir_url = "https://stores.guitarcenter.com/" + url
            sub_dir_response = session.get(full_subdir_url)
            dir_dom = etree.HTML(sub_dir_response.text)
            all_locations_urls += dir_dom.xpath(
                '//a[@data-ya-track="visit_page"]/@href'
            )
            sub_directories_urls = dir_dom.xpath(
                '//a[@class="Directory-listLink"]/@href'
            )
            sub_directories_urls += dir_dom.xpath(
                '//a[@class="Teaser-titleLink"]/@href'
            )
            for url in sub_directories_urls:
                if not url.endswith(".html"):
                    all_locations_urls.append(url)
                else:
                    full_sub2dir_url = "https://stores.guitarcenter.com/" + url
                    sub2dir_response = session.get(full_sub2dir_url)
                    sub2dir_dom = etree.HTML(sub2dir_response.text)
                    all_locations_urls += sub2dir_dom.xpath(
                        '//a[@data-ya-track="visit_page"]/@href'
                    )
                    sub2directories_urls = sub2dir_dom.xpath(
                        '//a[@class="Directory-listLink"]/@href'
                    )
                    sub2directories_urls += sub2dir_dom.xpath(
                        '//a[@class="Teaser-titleLink"]/@href'
                    )
                    for url in sub2directories_urls:
                        if not url.endswith(".html"):
                            all_locations_urls.append(url)

    for url in all_locations_urls:
        full_location_url = "https://stores.guitarcenter.com/" + url.replace("../", "")
        location_response = session.get(full_location_url)
        location_dom = etree.HTML(location_response.text)

        store_url = full_location_url
        store_url = store_url if store_url else "<MISSING>"
        location_name = location_dom.xpath('//h1[@id="location-name"]//text()')
        location_name = " ".join(location_name) if location_name else "<MISSING>"
        street_address = location_dom.xpath(
            '//meta[@itemprop="streetAddress"]/@content'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = location_dom.xpath(
            '//address[@id="address"]//span[@class="c-address-city"]//text()'
        )
        city = city[0] if city else "<MISSING>"
        state = location_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = location_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = location_dom.xpath('//address[@id="address"]/@data-country')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = location_dom.xpath('//div[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = location_dom.xpath("//main/@itemtype")
        location_type = (
            location_type[0].split("/")[-1] if location_type else "<MISSING>"
        )
        latitude = location_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = location_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = location_dom.xpath(
            '//table[@class="c-hours-details"]//text()'
        )
        hours_of_operation = (
            " ".join(hours_of_operation[1:]).replace("Hours", "").replace("hours", "")
            if hours_of_operation
            else "<MISSING>"
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
