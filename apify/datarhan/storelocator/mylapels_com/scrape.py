import re
import csv
import json
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "mylapels.com"
    start_url = "https://mylapels.com/store-locator/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="maplistko-js-extra"]/text()')[0]
    data = re.findall("ParamsKo =(.+);", data)[0]
    data = json.loads(data)

    for poi in data["KOObject"][0]["locations"]:
        store_url = urljoin(start_url, poi["locationUrl"])
        if "http" not in poi["locationUrl"]:
            store_url = "https://mylapels.com/location{}".format(poi["locationUrl"])
        store_url = store_url.replace("/ww.", "/www.")
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//div[@id="MapAddress"]/p/text()')
        if not address_raw:
            address_raw = loc_dom.xpath('//div[@id="MapDescription"]/p/text()')
        if not address_raw:
            address_raw = loc_dom.xpath(
                '//p[a[contains(@href, "tel")]]/following-sibling::p[1]/text()'
            )
        if len(address_raw) == 1:
            address_raw = address_raw[0].split(", ")
        if len(address_raw) == 4:
            address_raw = [" ".join(address_raw[:2])] + address_raw[2:]
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if not address_raw:
            address_raw = etree.HTML(poi["description"])
            address_raw = address_raw.xpath('.//div[@class="address"]/p/text()')
            address_raw = [elem.strip() for elem in address_raw if elem.strip()]
            if len(address_raw) == 1:
                address_raw = address_raw[0].split(", ")
        if address_raw:
            for elem in [
                "Lapels Dry Cleaning",
                "1036",
                "12623",
                "1581",
                "150 ",
                "8240 ",
                "395 ",
                "446 ",
                "209 ",
                "3038 ",
                "277 ",
            ]:
                if elem in address_raw[0]:
                    address_raw = address_raw[1:]
        if address_raw[-1] == "United States":
            address_raw = address_raw[:-1]
        if len(address_raw) == 1:
            address_raw = address_raw[0].split(", ")
        if len(address_raw) > 1:
            if "Suit" in address_raw[1]:
                address_raw = [", ".join(address_raw)[:2]] + address_raw[2:]
        if not address_raw:
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = location_name.split(", ")[-1]
            zip_code = "<MISSING>"
        else:
            street_address = address_raw[0]
            city = address_raw[1]
            state = location_name.split(", ")[-1]
            zip_code = "<MISSING>"
            if len(address_raw) > 2:
                zip_code = address_raw[2]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        poi_html = etree.HTML(poi["description"])
        phone = poi_html.xpath('//a[contains(@href, "tel")]/text()')
        phone = " ".join(phone[0].split()[1:]) if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

        if "Lapels Dry" in state:
            if len(zip_code.split()) == 2:
                state = zip_code.split()[0]
                zip_code = zip_code.split()[-1]
        if len(city.split(", ")) == 2:
            state = city.split(", ")[-1].split()[0]
            zip_code = city.split(", ")[-1].split()[-1]
            city = city.split(", ")[0]
        if "Lapels Dry" in state:
            state = "<MISSING>"
        state = state.split()[0]
        if city.split()[-1].isdigit():
            zip_code = city.split()[-1]
            city = city.split()[0].replace(",", "").strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = city.split(",")[0]
        zip_code = zip_code.split()[-1]
        if not zip_code.isdigit():
            zip_code = "<MISSING>"
        if state.isdigit():
            state = "<MISSING>"
            if ", " in street_address:
                state = street_address.split(", ")[-1]
        if city.isdigit():
            city = location_name.split(",")[0].split("Cleaning")[-1]

        street_address = street_address.split("\n")[0]
        if ", " in location_name:
            state = location_name.split(",")[-1].strip()
            city = (
                location_name.split(",")[0].strip().replace("Lapels Dry Cleaning ", "")
            )
        state = state.split()[0]
        city = city.split("(")[0].strip()
        if len(city) == 2:
            if "Tampa" in street_address:
                city = "Tampa"
                street_address = street_address.replace(city, "")
                state = "FL"
        if len(street_address.strip()) == 2:
            street_address = ", ".join(
                loc_dom.xpath(
                    '//div[a[contains(@href, "tel")]]/following-sibling::p[1]/text()'
                )[0].split(", ")[:2]
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
