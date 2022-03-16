import csv
from lxml import etree

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
    items = []
    scraped_items = []

    session = SgRequests()

    DOMAIN = "diddikicks.co.uk"
    start_url = "https://diddikicks.co.uk/find-us.php"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath('//div[@class="dropdown-content riffickmed"]/a/@href')
    all_locations = [url for url in all_urls if "http" in url]

    for store_url in list(set(all_locations)):
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        address_raw = loc_dom.xpath(
            '//h4[contains(text(), "Location:")]/following-sibling::p/text()'
        )
        if not address_raw:
            continue
        address_raw = address_raw[1]
        addr = parse_address_intl(address_raw)
        location_name = "{} Dids".format(address_raw.split(",")[0].strip())
        location_name = location_name if location_name else "<MISSING>"
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_2 + " " + addr.street_address_1
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = (
            loc_dom.xpath('//div[@class="footer-info"]/strong/text()')[0]
            .split("Tel: ")[-1]
            .strip()
        )
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
