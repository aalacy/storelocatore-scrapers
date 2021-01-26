import csv
import pyap
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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "covance.com"
    start_url = "https://www.covance.com/locations.html"

    hdr = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="locations-results-row"]')

    for poi_html in all_locations[1:]:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//li[@class="name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//li[@class="address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        full_addr = " ".join(raw_address).replace("\n", " ").replace("\t", " ")
        addr = pyap.parse(full_addr, country="GB")
        if "," not in poi_html.xpath('.//li[@class="title"]/text()')[0]:
            if "Bristol" not in poi_html.xpath('.//li[@class="title"]/text()')[0]:
                if not addr:
                    continue
        country_code = "<MISSING>"
        if "USA" in raw_address[-1]:
            country_code = "USA"
            raw_address = raw_address[:-1] + [" ".join(raw_address[-1].split()[:-1])]
        country_code = "<MISSING>"
        city = poi_html.xpath('.//li[@class="title"]/text()')[0].split(", ")[0]
        city = city.replace("CRU", "").strip() if city else "<MISSING>"
        street_address = (
            raw_address[0].replace(city, "").replace("\n", " ").replace("\t", " ")
        )
        state = (
            poi_html.xpath('.//li[@class="title"]/text()')[0].split(", ")[-1].strip()
        )
        street_address = street_address.split(", {}".format(state))[0]
        zip_code = raw_address[-1].split()[-1]
        if len(zip_code) == 3:
            zip_code = " ".join(raw_address[-1].split()[-2:])
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//li[@class="phone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        if zip_code in street_address:
            street_address = street_address.replace(zip_code, "")

        for elem in ["UK", "FAX", "England", "Kingdom"]:
            if elem in zip_code:
                zip_code = "<MISSING>"
        if city == state:
            state = "<MISSING>"
        if state == "Maidenhead":
            state = "<MISSING>"
            zip_code = "<MISSING>"

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
        check = f"{street_address} {city}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
