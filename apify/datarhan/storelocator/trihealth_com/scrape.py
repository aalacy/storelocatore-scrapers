import re
import csv
from lxml import etree
from urllib.parse import urljoin

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

    DOMAIN = "trihealth.com"
    start_urls = [
        "https://www.trihealth.com/hospitals-and-practices/",
        "https://www.trihealth.com/institutes-and-services/",
    ]
    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//table[@dropzone="copy"]//ul/li/a/@href')
        all_locations += dom.xpath('//a[contains(text(), "Locations")]/@href')
        all_locations += dom.xpath(
            '//li[a[contains(text(), "HOSPITALS & LOCATIONS")]]/ul//a/@href'
        )
        all_locations += dom.xpath(
            '//div[h1[contains(text(), "Institutes & Services")]]//a/@href'
        )
        all_locations += dom.xpath('//a[contains(text(), "Locations")]/@href')

    final_list = all_locations
    for url in list(set(all_locations)):
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        final_list += dom.xpath('//a[contains(text(), "Locations")]/@href')
        final_list += dom.xpath('//a[contains(@href, "/locations/")]/@href')

    final_list += [
        "https://www.trihealth.com/institutes-and-services/trihealth-orthopedic-and-sports-institute/locations#ANDERSON (7794 Five Mile Road)",
        "https://www.trihealth.com/institutes-and-services/trihealth-orthopedic-and-sports-institute/locations",
    ]
    for url in list(set(final_list)):
        store_url = urljoin(start_url, url)
        if "cgha.com" in url:
            continue
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        loc_type_1 = store_dom.xpath('//div[contains(@id, "prLoc")]')
        loc_type_2 = store_dom.xpath('//address[@class="vcard"]')
        loc_type_3 = store_dom.xpath('//main[h2[contains(text(), "Our Offices:")]]/p')
        loc_type_4 = store_dom.xpath('//td[strong[a[contains(@id, "anchor")]]]')
        directions_url = store_dom.xpath(
            '//a[contains(text(), "Directions and Parking")]/@href'
        )
        if loc_type_1:
            for loc_1 in loc_type_1:
                location_name = loc_1.xpath(".//h3/text()")[0]
                address_raw = loc_1.xpath(".//p/text()")
                address_raw = [elem.strip() for elem in address_raw if elem.strip()]
                street_address = address_raw[0]
                city = address_raw[1].split(",")[0]
                state = address_raw[1].split(",")[-1].split()[0].strip()
                zip_code = address_raw[1].split(",")[-1].split()[-1].strip()
                country_code = "<MISSING>"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                phone = address_raw[-1]
                geo = re.findall("@(.+),17z", loc_1.xpath(".//a/@href")[0])
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                if geo:
                    geo = geo[0].split(",")
                    latitude = geo[0]
                    longitude = geo[-1]
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
        if loc_type_2 and not directions_url:
            for loc_2 in loc_type_2:
                location_name = loc_2.xpath('.//div[@class="fn org"]//text()')
                if not location_name:
                    continue
                location_name = location_name[0]
                street_address = loc_2.xpath('.//span[@class="street-address"]/text()')
                if not street_address:
                    continue
                street_address = street_address[0].strip()
                city = loc_2.xpath('.//span[@class="locality"]/text()')[0]
                state = loc_2.xpath('.//span[@class="region"]/text()')[0]
                zip_code = loc_2.xpath('.//span[@class="postal-code"]/text()')[0]
                country_code = "<MISSING>"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                phone = loc_2.xpath(
                    './/div[@class="tel subtle"]/span[@class="value"]/span[1]/text()'
                )
                if not phone:
                    phone = store_dom.xpath(
                        '//div[@class="tel "]/span[@class="value"]/span[1]/text()'
                    )
                    if phone:
                        phone = [phone[0].strip().split(":")[-1]]
                phone = phone[0] if phone else "<MiSSING>"
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
        if loc_type_3:
            for loc_3 in loc_type_3:
                location_name = loc_3.xpath(".//a/strong/text()")
                location_name = location_name[0] if location_name else ""
                if not location_name:
                    continue
                address_raw = loc_3.xpath("text()")
                address_raw = [
                    elem.strip() for elem in address_raw if elem.strip() and elem != "."
                ]
                street_address = address_raw[0]
                city = address_raw[1].split(",")[0]
                state = address_raw[1].split(",")[-1].split()[0]
                zip_code = address_raw[1].split(",")[-1].split()[-1]
                country_code = "<MISSING>"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                phone = address_raw[2].split(": ")[-1]
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
        if directions_url:
            directions_response = session.get(
                "https://www.trihealth.com" + directions_url[0]
            )
            directions_dom = etree.HTML(directions_response.text)
            all_dir_locs = directions_dom.xpath("//main//tbody/tr")
            if all_dir_locs:
                for dir_loc in all_dir_locs:
                    location_name = dir_loc.xpath("./td[1]//strong/text()")[0]
                    address_raw = dir_loc.xpath("./td[1]/p/text()")
                    if not address_raw:
                        address_raw = dir_loc.xpath("./td[1]/span/text()")
                    if not address_raw:
                        address_raw = dir_loc.xpath("./td[1]/text()")
                    if not address_raw:
                        address_raw = dir_loc.xpath("./td[1]/text()")
                    address_raw = [elem.strip() for elem in address_raw if elem.strip()]
                    if len(address_raw) == 3:
                        address_raw = [" ".join(address_raw[:2])] + address_raw[2:]
                    street_address = address_raw[0].strip()
                    city = address_raw[1].strip().split(",")[0]
                    state = address_raw[1].strip().split(",")[-1].split()[0]
                    zip_code = address_raw[1].strip().split(",")[-1].split()[-1]
                    country_code = "<MISSING>"
                    store_number = "<MISSING>"
                    phone = dir_loc.xpath("./td[2]/span/text()")
                    if not phone:
                        phone = dir_loc.xpath("./td[2]/p/text()")
                    phone = phone[0] if phone else "<MISSING>"
                    if len(phone.strip()) < 3:
                        phone = "<MISSING>"
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
            loc_type_2 = store_dom.xpath('//address[@class="vcard"]')
            for loc_2 in loc_type_2:
                location_name = loc_2.xpath('.//div[@class="fn org"]//text()')
                if not location_name:
                    continue
                location_name = location_name[0]
                street_address = loc_2.xpath('.//span[@class="street-address"]/text()')
                if not street_address:
                    continue
                street_address = street_address[0].strip()
                city = loc_2.xpath('.//span[@class="locality"]/text()')[0]
                state = loc_2.xpath('.//span[@class="region"]/text()')[0]
                zip_code = loc_2.xpath('.//span[@class="postal-code"]/text()')[0]
                country_code = "<MISSING>"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                phone = loc_2.xpath(
                    './/div[@class="tel subtle"]/span[@class="value"]/span[1]/text()'
                )[0]
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

        if loc_type_4:
            for loc_4 in loc_type_4:
                location_name = loc_4.xpath(".//a/@name")
                location_name = location_name[0] if location_name else "<MISSING>"
                address_raw = loc_4.xpath(".//text()")
                address_raw = [elem.strip() for elem in address_raw if elem.strip()][
                    1:-2
                ]
                street_address = address_raw[0]
                city = address_raw[-1].split(", ")[0]
                state = address_raw[-1].split(", ")[-1].split()[0]
                zip_code = address_raw[-1].split(", ")[-1].split()[-1]
                country_code = "<MISSING>"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                phone = loc_4.xpath(".//text()")[-3].strip()
                geo = (
                    loc_4.xpath('.//a[contains(@href, "/maps/")]/@href')[0]
                    .split("/@")[-1]
                    .split(",")[:2]
                )
                latitude = geo[0].strip()
                longitude = geo[-1].strip().replace("\n", "").replace(" ", "")
                if geo:
                    geo = geo[0].split(",")
                    latitude = geo[0]
                    longitude = geo[-1]
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
