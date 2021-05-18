import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgFirefox
from sgscrape.sgpostal import parse_address_intl


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
    session = SgRequests(proxy_rotation_failure_threshold=0).requests_retry_session(
        retries=2, backoff_factor=0.3
    )

    items = []
    scraped_items = []
    scraped_urls = []

    DOMAIN = "mylapels.com"
    start_url = "https://mylapels.com/store-locator/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="maplistko-js-extra"]/text()')[0]
    data = re.findall("ParamsKo =(.+);", data)[0]
    data = json.loads(data)

    for poi in data["KOObject"][0]["locations"]:
        store_url = urljoin(start_url, poi["locationUrl"])
        if "http" not in poi["locationUrl"]:
            store_url = "https://mylapels.com/location{}".format(poi["locationUrl"])
        store_url = store_url.replace("/ww.", "/www.")
        if store_url in scraped_urls:
            continue
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        if loc_dom.xpath('//div[@id="error-404"]'):
            store_url = store_url.replace("/locations/", "/location/")
            with SgFirefox() as driver:
                driver.get(store_url)
                loc_dom = etree.HTML(driver.page_source)
        poi_page = loc_dom.xpath('//script[contains(text(), "StreetAddress")]/text()')
        if poi_page:
            poi_page = json.loads(poi_page[0])
            location_name = poi_page["Name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi_page["Address"]["StreetAddress"]
            city = poi_page["Address"]["AddressLocality"]
            state = poi_page["Address"]["AddressRegion"]
            zip_code = poi_page["Address"]["PostalCode"]
            country_code = poi_page["Address"]["AddressCountry"]
            location_type = poi_page["@type"]
        else:
            location_name = poi["title"]
            location_name = location_name if location_name else "<MISSING>"
            if poi["address"]:
                raw_address = etree.HTML(poi["address"]).xpath("//text()")
            else:
                raw_address = loc_dom.xpath('//div[@id="MapDescription"]/p/text()')
                raw_address = [e.strip() for e in raw_address]
            addr = parse_address_intl(" ".join(raw_address))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            city = city if city else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = addr.country
            country_code = country_code if country_code else "<MISSING>"
            location_type = "<MISSING>"
        store_number = "<MISSING>"
        poi_html = etree.HTML(poi["description"])
        phone = poi_html.xpath('//a[contains(@href, "tel")]/text()')
        phone = " ".join(phone[0].split()[1:]) if phone else "<MISSING>"
        if phone == "<MISSING>":
            phone = loc_dom.xpath('//p[contains(text(), "please call")]/strong/text()')
            phone = phone[0] if phone else "<MISSING>"
        if phone == "<MISSING>":
            phone = loc_dom.xpath(
                '//h1[contains(text(), "{}")]/following-sibling::p[1]/a/text()'.format(
                    location_name
                )
            )
            phone = phone[0] if phone else "<MISSING>"
        if phone == "<MISSING>":
            phone = loc_dom.xpath(
                '//p[span[contains(text(), "{}")]]/following-sibling::p[1]//a/text()'.format(
                    street_address
                )
            )
            phone = phone[0] if phone else "<MISSING>"
        if phone == "<MISSING>":
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else "<MISSING>"
        if phone == "<MISSING>":
            phone = loc_dom.xpath(
                '//p[contains(text(), "{}")]/text()'.format(street_address)
            )
            phone = [e.strip() for e in phone if "(" in e]
            phone = phone[0] if phone else "<MISSING>"
        if phone == "<MISSING>":
            phone = loc_dom.xpath(
                '//p[contains(text(), "{}")]/text()'.format(street_address)
            )
            phone = phone[-1].strip() if phone and "-" in phone[-1] else "<MISSING>"
        if phone == "<MISSING>":
            phone = loc_dom.xpath('//p[contains(text(), "{}")]/text()'.format(city))
            phone = phone[-1].strip() if phone and "-" in phone[-1] else "<MISSING>"
        if phone == "<MISSING>":
            phone = loc_dom.xpath(
                '//p[contains(text(), "{}")]/preceding-sibling::div[1]/a/text()'.format(
                    city
                )
            )
            phone = phone[0].strip() if phone else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

        add_address = loc_dom.xpath(
            '//div[@class=" uavc-icons-center uavc-icons "]/preceding-sibling::p[1]/text()'
        )
        if add_address:
            addr = parse_address_intl(add_address[0])
            if zip_code == "<MISSING>":
                zip_code = addr.postcode
                zip_code = zip_code if zip_code else "<MISSING>"
            if city == "<MISSING>":
                city = addr.city
                city = city if city else "<MISSING>"
            if country_code == "<MISSING>":
                country_code = addr.country
                country_code = country_code if country_code else "<MISSING>"
        if state == "<MISSING>":
            if "," in location_name:
                state = location_name.split(",")[-1].split("(")[0].strip()

        if street_address == "277 W Reynolds St 277 West Reynolds Street":
            street_address = "277 West Reynolds Street"

        if state == "<MISSING>" and "Boston" in location_name:
            state = "MA"
        if city == "<MISSING>" and "Westwood" in location_name:
            city = "Westwood"
        if city == "<MISSING>" and "Cohasset" in street_address:
            city = "Cohasset"
            street_address = street_address.replace("Cohasset", "")

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
        if store_url not in scraped_urls:
            scraped_urls.append(store_url)

        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
