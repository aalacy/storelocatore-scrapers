import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "ketteringhealth.org"
    start_url = "https://ketteringhealth.org/wp-json/facetwp/v1/refresh"

    hdr = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    }
    page = 1
    frm = {
        "action": "facetwp_refresh",
        "data": {
            "facets": {
                "count_locations": [],
                "l_search": "",
                "location_type": [],
                "services": [],
                "distance": [],
                "load_more": [],
                "locations_map": [],
                "paged": page,
            },
            "frozen_facets": {"distance": "hard", "locations_map": "hard"},
            "http_params": {"get": [], "uri": "locations", "url_vars": []},
            "template": "locations",
            "extras": {"sort": "default"},
            "soft_refresh": 1,
            "is_bfcache": 1,
            "first_load": 0,
            "paged": page,
        },
    }
    response = session.post(start_url, json=frm, headers=hdr)
    data = json.loads(response.text)
    total_pages = data["settings"]["pager"]["total_pages"]

    dom = etree.HTML(data["template"])
    all_locations = dom.xpath('//a[@class="directory-card"]/@href')

    for page in range(2, total_pages + 1):
        frm["data"]["facets"]["paged"] = page
        frm["data"]["paged"] = page
        response = session.post(start_url, json=frm, headers=hdr)
        data = json.loads(response.text)
        dom = etree.HTML(data["template"])
        all_locations += dom.xpath('//a[@class="directory-card"]/@href')

    for store_url in list(set(all_locations)):
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="heading-1"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@class="profile-content"]/address//text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        addr = parse_address_intl(" ".join(raw_address))

        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="contact-info"]/p/a/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        geo = loc_dom.xpath('//address/p/a[contains(@href, "maps")]/@href')
        if geo:
            geo = geo[0].split("query=")[-1].split("&")[0].split(",")
            latitude = geo[0]
            longitude = geo[1]
        hoo = loc_dom.xpath('//ul[@class="hours-list"]//text()')
        if hoo:
            hoo = [e.strip() for e in hoo if e.strip()]
        if len(hoo) == 0:
            hoo = loc_dom.xpath(
                '//div[@class="profile-content"]//div[@class="hours-info"]//text()'
            )
        hoo = [e.strip() for e in hoo if e.strip()]
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
        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
