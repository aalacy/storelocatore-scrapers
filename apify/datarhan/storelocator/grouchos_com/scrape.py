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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "grouchos.com"
    start_url = "https://www.grouchos.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[@class="btn btn-xs btn-white website"]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        name = loc_dom.xpath("//title/text()")
        loc_id = loc_dom.xpath('//div[contains(@id, "contact-form-widget")]/@id')[
            0
        ].replace("contact-form-widget-", "")
        loc_response = session.get(
            f"https://impact.locable.com/widgets/contact_form_widgets/{loc_id}"
        )
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h3[@itemprop="name"]/text()')
        if not location_name:
            location_name = name
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//a[@itemprop="address"]/span/text()')
        raw_address = [elem.strip() for elem in raw_address]
        street_address = raw_address[0]
        location_type = "<MISSING>"
        state = raw_address[-1].split(", ")[-1].split()[0]
        city = raw_address[-1].split(", ")[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        geo = (
            loc_dom.xpath('//a[@itemprop="address"]/@href')[0].split("=")[-1].split(",")
        )
        latitude = geo[0]
        longitude = geo[1]
        hours_of_operation = loc_dom.xpath('//div[@itemprop="openingHours"]//text()')
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
