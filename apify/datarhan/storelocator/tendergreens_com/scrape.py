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

    DOMAIN = "tendergreens.com"
    start_url = "https://www.tendergreens.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(@href, "/locations/")]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//div[@class="location-info__left"]/h2[@class="uc"]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@class="location-info__address"]/p/text()')
        if len(raw_address) == 3:
            raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = loc_dom.xpath('//p[@class="location-info__phone large"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        geo = loc_dom.xpath('//a[contains(@href, "google.com/maps")]/@href')[0]
        if "/@" in geo:
            geo = geo.split("/@")[-1].split(",")[:2]
        else:
            try:
                geo = geo.split("ll=")[1].split("&")[0].split(",")
            except Exception:
                geo = ""
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            latitude = geo[0]
            longitude = geo[1]
        hours_of_operation = loc_dom.xpath(
            '//table[@class="location-info__hours"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation).split("inconvenience. ")[-1]
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
