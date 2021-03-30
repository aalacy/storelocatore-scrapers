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

    DOMAIN = "seacoastbank.com"
    start_url = "https://www.seacoastbank.com/locations/all"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//h2[@class="c-person-callout_name"]/center/a/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
        poi = json.loads(
            poi.replace("/winter-park", '/winter-park",').replace(',",', ",")
        )

        location_name = loc_dom.xpath(
            '//h1[@class="c-location_name u-headline-gradient"]/text()'
        )
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = poi[0]["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi[0]["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi[0]["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi[0]["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi[0]["address"]["addressCountry"]["name"]
        store_number = "<MISSING>"
        phone = poi[0]["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi[0]["@type"]
        latitude = poi[0]["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi[0]["geo"]["longitude"]
        longitude = longitude.replace("--", "-") if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath('//table[@class="c-info-table"]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = " ".join(hours_of_operation).replace("Drive Thru", "")
        p_1_1 = loc_dom.xpath(
            '//table[@class="c-info-table"]/tbody/tr[1]/td[1]/text()'
        )[0].strip()
        p_1_2 = loc_dom.xpath(
            '//table[@class="c-info-table"]/tbody/tr[1]/td[2]/text()'
        )[0].strip()
        p_2_1 = ""
        p_2_2 = ""
        if loc_dom.xpath('//table[@class="c-info-table"]/tbody/tr[2]/td[1]/text()'):
            p_2_1 = loc_dom.xpath(
                '//table[@class="c-info-table"]/tbody/tr[2]/td[1]/text()'
            )[0].strip()
            p_2_2 = loc_dom.xpath(
                '//table[@class="c-info-table"]/tbody/tr[2]/td[2]/text()'
            )[0].strip()
        p_3_1 = ""
        p_3_2 = ""
        if loc_dom.xpath('//table[@class="c-info-table"]/tbody/tr[3]/td[1]/text()'):
            p_3_1 = loc_dom.xpath(
                '//table[@class="c-info-table"]/tbody/tr[3]/td[1]/text()'
            )[0].strip()
            p_3_2 = loc_dom.xpath(
                '//table[@class="c-info-table"]/tbody/tr[3]/td[2]/text()'
            )[0].strip()
        hours_of_operation = f"{p_1_1} {p_1_2} {p_2_1} {p_2_2} {p_3_1} {p_3_2}".strip()

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
