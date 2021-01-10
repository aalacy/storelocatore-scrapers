import re
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
    scraped_items = []

    DOMAIN = "westamerica.com"
    start_url = "https://www.westamerica.com/about/locations/"
    response = session.post(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[contains(@class, "tve_faq")]')
    for city_html in all_locations:
        sub_locs_names = city_html.xpath(".//h2/text()")
        for location_name in sub_locs_names:
            all_elements = city_html.xpath(
                '//h2[contains(text(), "%s")]/following-sibling::*' % location_name
            )
            all_sub_locs = []
            for elem in all_elements:
                if elem.tag == "h2":
                    break
                all_sub_locs.append(elem)

            all_sub_addresses = []
            all_geo = []
            for elem in all_sub_locs:
                sub_address = elem.xpath(".//a/text()")
                if not sub_address:
                    continue
                all_sub_addresses.append(sub_address)

                geo = elem.xpath('.//a[contains(@href, "sll")]/@href')
                if geo:
                    all_geo.append(geo)

            all_sub_hours = []
            for elem in all_elements:
                sub_hoo = elem.xpath(".//text()")
                if not sub_hoo:
                    continue
                sub_hoo = " ".join(sub_hoo)
                if "Monday" in sub_hoo:
                    all_sub_hours.append(elem.xpath(".//text()"))

            for i, sub_address in enumerate(all_sub_addresses):
                store_url = "<MISSING>"
                street_address = sub_address[0]
                city = location_name
                state = "CA"
                zip_code = "<MISSING>"
                country_code = "<MISSING>"
                store_number = "<MISSING>"
                phone = sub_address[-1].split(",")[-1].split(" (")[-1]
                if not phone.startswith("("):
                    phone = "(" + phone
                street_address = street_address.replace(phone, "")
                location_type = "<MISSING>"
                if "ATM" in phone:
                    location_type = "ATM"
                    phone = "<MISSING>"
                try:
                    latitude = (
                        all_geo[i][-1].split("sll=")[-1].split("&")[0].split(",")[0]
                    )
                    longitude = (
                        all_geo[i][-1].split("sll=")[-1].split("&")[0].split(",")[-1]
                    )
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                try:
                    hours_of_operation = " ".join(all_sub_hours[i])
                    hours_of_operation = hours_of_operation.replace(
                        "Lobby Hours:", ""
                    ).strip()
                    hours_of_operation = re.findall(
                        "(.+Sunday: Closed)", hours_of_operation
                    )[0]
                except:
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
