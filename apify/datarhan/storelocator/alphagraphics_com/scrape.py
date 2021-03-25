import csv
from lxml import etree
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

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
    session = SgRequests().requests_retry_session(retries=3, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "alphagraphics.com"
    start_url = "https://printing-services-near-me.alphagraphics.com/search.html?q={}"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//ol[@class="ResultList"]//a[@data-ya-track="website_cta"]/@href'
        )

    for store_url in list(set(all_locations)):
        if not store_url.strip():
            continue
        if "html" in store_url:
            store_url = (
                "/".join(store_url.split("/")[:-1])
                + "/"
                + store_url.split("/")[-1].replace(".", "").replace("html", ".html")
            )
        if "alphagraphics.com" not in store_url:
            continue
        loc_response = session.get(store_url)
        if loc_response.status_code != 200:
            continue
        if "alphagraphics.com" not in loc_response.url:
            continue
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="location-heading"]/text()')
        if not location_name:
            location_name = loc_dom.xpath(
                '//div[@class="wpb_content_element"]/h2/text()'
            )
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        if not street_address:
            street_address = loc_dom.xpath(
                '//div[@class="wpb_content_element"]/p[1]/text()'
            )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        if not city:
            city = loc_dom.xpath('//div[@class="wpb_content_element"]/p[1]/text()')[
                -1
            ].split(", ")
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        if not state:
            state = [
                loc_dom.xpath('//div[@class="wpb_content_element"]/p[1]/text()')[-1]
                .split(", ")[-1]
                .split()[0]
            ]
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        if not zip_code:
            zip_code = [
                loc_dom.xpath('//div[@class="wpb_content_element"]/p[1]/text()')[-1]
                .split(", ")[-1]
                .split()[-1]
            ]
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = loc_dom.xpath('//span[@itemprop="addressCountry"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="location-content--hours"]//text()')
        if not hoo:
            hoo = loc_dom.xpath('//div[@class="wpb_content_element"]/p[2]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
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
        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
