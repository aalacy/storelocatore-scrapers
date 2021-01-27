import csv
import json
import usaddress
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

    DOMAIN = "lamichoacanameatmarket.com"
    start_url = "https://www.lamichoacanameatmarket.com/wp-admin/admin-ajax.php"

    formdata = {
        "action": "store_wpress_listener",
        "method": "display_list",
        "page_number": "1",
        "lat": "",
        "lng": "",
        "category_id": "",
        "max_distance": "",
        "nb_display": "500",
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)
    dom = etree.HTML(data["stores"])
    all_locations = dom.xpath('//div[@class="ygp_sl_stores_list_box"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath(
            './/div[@class="ygp_sl_stores_list_more_info_box"]/a/@href'
        )
        store_url = (
            "https://www.lamichoacanameatmarket.com/tienda/" + store_url[0]
            if store_url
            else "<MISSING>"
        )
        location_name = poi_html.xpath('.//a[@class="ygp_sl_stores_list_name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath(
            './/div[@class="ygp_sl_stores_list_address"]/text()'
        )[0].split(", ")

        raw_address = [elem.strip() for elem in raw_address]
        if raw_address[-1] == "Estados Unidos":
            raw_address = raw_address[:-1]
        if len(raw_address) == 4:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0]
        raw_addr = poi_html.xpath('.//div[@class="ygp_sl_stores_list_address"]/text()')[
            0
        ]
        if "Estados Unidos" in raw_addr:
            raw_addr = raw_addr.replace(", Estados Unidos", "")
        usaddress_data = usaddress.tag(raw_addr)
        city = usaddress_data[0]["PlaceName"]
        state = usaddress_data[0]["StateName"]
        str_indx = street_address.split()
        street_address = " ".join(sorted(set(str_indx), key=str_indx.index))
        zip_code = usaddress_data[0]["ZipCode"]
        country_code = "<MISSING>"
        store_number = store_url.split("=")[-1]
        phone = poi_html.xpath('.//div[@class="ygp_sl_stores_list_tel"]/text()')
        phone = phone[0].split(" y")[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = poi_html.xpath(".//img/@src")[0].split("=")[1].split("&")[0].split(",")
        latitude = geo[0]
        longitude = geo[1]

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        hours_of_operation = loc_dom.xpath(
            '//h2[contains(text(), "HORARIOS")]/following-sibling::p[1]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
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
