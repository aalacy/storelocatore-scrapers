import csv
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "mortons.com"
    start_url = "https://www.mortons.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//table[@id="location_listing"]//li/a/@href')[:-7]

    for store_url in all_locations:
        if "mortons.com" not in store_url:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@id="content"]/h1/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//td[strong[contains(text(), "Address")]]/text()')
        addres_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if addres_raw[1].split()[0][0].isdigit():
            addres_raw = [", ".join(addres_raw[:2])] + addres_raw[2:]
        if "The Shops" in addres_raw[0]:
            addres_raw = addres_raw[1:]
        street_address = addres_raw[0]
        city = addres_raw[1].split(", ")[0]
        state = addres_raw[1].split(", ")[-1].split()[0]
        zip_code = addres_raw[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = [elem for elem in addres_raw if "phone" in elem.lower()]
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if loc_dom.xpath('//iframe[@title="Google Map"]/@src'):
            geo = (
                loc_dom.xpath('//iframe[@title="Google Map"]/@src')[0]
                .split("&ll=")[-1]
                .split("&")[0]
                .split(",")
            )
            if len(geo) == 2:
                latitude = geo[0]
                longitude = geo[1]
        hours_of_operation = " ".join(addres_raw[4:])

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
