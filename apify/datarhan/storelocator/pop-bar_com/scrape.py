import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_urls = [
        "https://www.pop-bar.com/pages/united-states",
        "https://www.pop-bar.com/pages/canada",
    ]
    domain = "pop-bar.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = []
    for start_url in start_urls:
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="one-third-column"]/a/@href')
        all_locations += dom.xpath('//div[@class="one-column"]/a/@href')
        all_locations += dom.xpath('//div[@class="one-half-column"]/a/@href')

        for url in list(set(all_locations)):
            if not url:
                continue
            store_url = urljoin(start_url, url)
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            locations = loc_dom.xpath(
                '//div[@class="Faq locations"]/div[div[@class="Grid__Cell  1/2--tablet-and-up"]]'
            )
            for loc in locations:
                location_name = loc.xpath('.//h1[@class="Heading u-h1"]/text()')
                location_name = location_name[0] if location_name else "<MISSING>"
                raw_address = loc.xpath(
                    './/div[p[contains(text(), "Address")]]/following-sibling::div[1]/text()'
                )
                raw_address = [e.strip() for e in raw_address if e.strip()]
                addr = parse_address_intl(" ".join(raw_address))
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                street_address = street_address if street_address else "<MISSING>"
                street_address = street_address.split("(")[0].strip().replace("*", "")
                city = addr.city
                city = city.strip() if city else "<MISSING>"
                state = addr.state
                state = state if state else "<MISSING>"
                zip_code = addr.postcode
                zip_code = zip_code if zip_code else "<MISSING>"
                if city == "M9":
                    zip_code += " M9"
                    city = location_name
                if "united-states" in start_url:
                    country_code = "US"
                else:
                    country_code = "CA"
                country_code = country_code if country_code else "<MISSING>"
                store_number = "<MISSING>"
                phone = loc.xpath(
                    './/div[@class="store-hours"]/div[@class="paragraf"]/text()'
                )[-2].strip()
                if "," in phone:
                    phone = "<MISSING>"
                location_type = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hoo = loc.xpath(
                    './/div[@class="store-hours"]/div[@class="paragraf"][1]/text()'
                )
                hoo = [e.strip() for e in hoo if e.strip()]
                hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
                if "Pickup and delivery only " in hours_of_operation:
                    hours_of_operation = "<MISSING>"

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
