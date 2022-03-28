import re
import csv
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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
    session = SgRequests(proxy_rotation_failure_threshold=0)

    items = []
    scraped_items = []
    scraped_urls = []

    DOMAIN = "countryfinancial.com"
    start_url = "https://www.countryfinancial.com/services/forms?configNodePath=%2Fcontent%2Fcfin%2Fen%2Fjcr%3Acontent%2FrepLocator&cfLang=en&repSearchType=queryByLocation&repSearchValue={}"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=50
    )
    for code in all_codes:
        try:
            response = session.get(start_url.format(code), headers=hdr)
        except Exception:
            continue
        dom = etree.HTML(response.text)

        all_poi_html = dom.xpath('//div[@itemtype="//schema.org/Organization"]')
        for poi_html in all_poi_html:
            store_url = poi_html.xpath('.//a[@itemprop="url"]/@href')[0]
            if store_url in scraped_urls:
                continue
            loc_response = session.get(store_url)
            scraped_urls.append(store_url)
            loc_dom = etree.HTML(loc_response.text)
            poi = loc_dom.xpath('//script[contains(text(), "PostalAddress")]/text()')
            if not poi:
                continue
            poi = demjson.decode(poi[0].replace("\n", ""))

            data = loc_dom.xpath('//script[contains(text(), "JSContext")]/text()')[0]
            data = re.findall("JSContext =(.+);", data)[0]
            data = demjson.decode(data)

            location_name = poi[0]["name"].replace("&#39;", "'")
            street_address = data["profile"]["address"]["street"]
            suit = data["profile"]["address"].get("suite")
            if suit:
                street_address += " " + suit
            street_address = street_address if street_address else "<MISSING>"
            city = poi[0]["address"]["addressLocality"]
            city = city.replace("&#39;", "'") if city else "<MISSING>"
            state = poi[0]["address"]["addressRegion"]
            state = state if state else "<MISSING>"
            zip_code = poi[0]["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = poi[0]["contactPoint"][0]["telephone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi[0]["@type"]
            latitude = data["profile"]["latlng"]
            latitude = latitude[0] if latitude else "<MISSING>"
            longitude = data["profile"]["latlng"]
            longitude = longitude[1] if longitude else "<MISSING>"
            hours_of_operation = "<MISSING>"

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
