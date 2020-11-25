import csv
import sgzip
from lxml import etree
from sgzip import SearchableCountries

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

    DOMAIN = "countryfinancial.com"

    all_codes = []
    us_zips = sgzip.for_radius(radius=200, country_code=SearchableCountries.USA)
    for zip_code in us_zips:
        all_codes.append(zip_code)

    start_url = "https://www.countryfinancial.com/services/generic-forms?configNodePath=%2Fcontent%2Fcfin%2Fen%2Fjcr%3Acontent%2FrepLocator&repSearchType=location&cfLang=en&repSearchValue={}"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    for code in all_codes:
        try:
            response = session.get(start_url.format(code), headers=hdr)
        except Exception:
            continue
        dom = etree.HTML(response.text)

        all_poi_html = dom.xpath('//div[contains(@class, "repCard")]')
        for poi_html in all_poi_html:
            store_url = poi_html.xpath('.//div[@class="rep-info"]/a[1]/@href')
            store_url = (
                [elem.strip() for elem in store_url if elem.strip()][0]
                if store_url
                else "<MISSING>"
            )
            location_name = poi_html.xpath('.//img[@class="repImg"]/@alt')
            location_name = (
                " ".join(location_name).replace("\n", "").strip()
                if location_name
                else "<MISSING>"
            )
            street_address = poi_html.xpath('.//span[@itemprop="streetAddress"]/text()')
            street_address = (
                street_address[0].replace("\n", "").strip()
                if street_address
                else "<MISSING>"
            )
            city = poi_html.xpath('.//span[@itemprop="addressLocality"]/text()')
            city = city[0].replace("\n", "").strip() if city else "<MISSING>"
            state = poi_html.xpath('.//span[@itemprop="addressRegion"]/text()')
            state = state[0].replace("\n", "").strip() if state else "<MISSING>"
            zip_code = poi_html.xpath('.//span[@itemprop="postalCode"]/text()')
            zip_code = (
                zip_code[0].replace("\n", "").strip() if zip_code else "<MISSING>"
            )
            country_code = ""
            country_code = country_code if country_code else "<MISSING>"
            store_number = ""
            store_number = store_number if store_number else "<MISSING>"
            phone = poi_html.xpath('.//span[@itemprop="telephone"]/text()')
            phone = phone[0].replace("\n", "").strip() if phone else "<MISSING>"
            location_type = ""
            location_type = location_type if location_type else "<MISSING>"
            latitude = ""
            longitude = ""
            if poi_html.xpath("@data-geo"):
                latitude = poi_html.xpath("@data-geo")[0].split(",")[0]
                longitude = poi_html.xpath("@data-geo")[0].split(",")[-1]
            latitude = latitude.strip() if latitude else "<MISSING>"
            longitude = longitude.strip() if longitude else "<MISSING>"
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
            if location_name not in scraped_items:
                scraped_items.append(location_name)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
