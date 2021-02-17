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
    session = SgRequests()

    items = []

    DOMAIN = "patientfirst.com"
    start_url = "https://www.patientfirst.com/locations-sitemap.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    all_urls = []
    response = session.get(start_url, headers=headers)
    root = etree.fromstring(response.content)
    for sitemap in root:
        children = sitemap.getchildren()
        all_urls.append(children[0].text)

    for store_url in all_urls:
        store_response = session.get(store_url, headers=headers)
        store_dom = etree.HTML(store_response.text)

        location_name = store_dom.xpath('//div[@class="address-container"]/h1/text()')
        location_name = " ".join(location_name) if location_name else "<MISSING>"
        street_address = store_dom.xpath(
            '//h2[@class="centerAddress clearLeft mt-3 mb-1"]/text()'
        )[0]
        if len(store_dom.xpath('//h2[@class="centerAddress"]/text()')) == 2:
            street_address += (
                ", " + store_dom.xpath('//h2[@class="centerAddress"]/text()')[0]
            )
        street_address = street_address if street_address else "<MISSING>"
        city = store_dom.xpath('//h2[@class="centerAddress"]/text()')[-1].split(", ")[0]
        state = (
            store_dom.xpath('//h2[@class="centerAddress"]/text()')[-1]
            .split(", ")[-1]
            .split()[0]
        )
        zip_code = (
            store_dom.xpath('//h2[@class="centerAddress"]/text()')[-1]
            .split(", ")[-1]
            .split()[-1]
        )
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = store_dom.xpath('//span[@class="phoneandhours"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        location_type = location_type if location_type else "<MISSING>"
        geo = store_dom.xpath('//img[@id="mapimage"]/@src')[0].split("=")[-1].split(",")
        latitude = geo[0]
        longitude = geo[1]
        hours_of_operation = store_dom.xpath('//span[@class="phoneandhours"]/p/text()')
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        hours_of_operation = hours_of_operation.replace(
            "Regular and after hours medical care, ", ""
        )
        hours_of_operation = hours_of_operation.replace(
            ", including weekends and holidays", ""
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
