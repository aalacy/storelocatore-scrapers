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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "woodcraft.com"
    start_url = "https://www.woodcraft.com/store_locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="stores-by-state__store-link"]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//span[@itemprop="name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//p[@itemprop="address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = raw_address[2]
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//table[@class="table table--hours"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation).replace("Please Wear Mask", "")
            if hours_of_operation
            else "<MISSING>"
        )
        hours_of_operation = (
            hours_of_operation.replace(" Face mask required.", "")
            .replace("\n", "")
            .replace("Face Mask Required", "")
            .replace("Masks Required", "")
            .replace("Mask required", "")
            .replace("Face Masks Strongl", "")
            .replace("Face Masks Strong", "")
        )
        hours_of_operation = (
            hours_of_operation.replace("Face Masks Strong ", "")
            .replace("Face Mask Require", "")
            .replace("masks required", "")
            .replace("Open to the public", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace("\r", "")
        )

        str_to_del = [
            "Shoppes of New Castle ",
            "Parkway Shopping Center ",
            "Overland Park Shopping Center ",
            "Tri-County Towne Center ",
            "Battlefield Shopping Center ",
            "Hunnington Place, ",
            "Shoppes of New Castle ",
            "Towne Square Shopping Center Next to Sams ",
            "Ravensworth Shopping Center ",
            "Henrietta Plaza ",
        ]
        for elem in str_to_del:
            street_address = street_address.replace(elem, "")
        street_address = street_address.split(", use")[0]

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
