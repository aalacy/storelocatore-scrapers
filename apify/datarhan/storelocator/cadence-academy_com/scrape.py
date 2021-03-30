import re
import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgFirefox


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

    DOMAIN = "cadence-education.com"
    start_url = "https://www.cadence-education.com/locations/"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
        all_locations = dom.xpath(
            '//script[contains(text(), "cadence_location_object")]/text()'
        )[0]
        all_locations = re.findall("cadence_location_object = (.+);", all_locations)[0]
        all_locations = json.loads(all_locations)

    for poi in all_locations["locations_data"]:
        street_address = poi["street_name"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state_short"]
        state = state if state else "<MISSING>"
        zip_code = poi["post_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country_short"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["post_id"]
        store_number = store_number if store_number else "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"

        post_url = "https://www.cadence-education.com/wp-admin/admin-ajax.php"
        formdata = {
            "action": "fetch_locations",
            "post_ids[]": store_number,
            "locations_data[0][address]": poi["address"],
            "locations_data[0][city]": poi["city"],
            "locations_data[0][country]": poi["country"],
            "locations_data[0][country_short]": poi["country_short"],
            "locations_data[0][lat]": poi["lat"],
            "locations_data[0][lng]": poi["lng"],
            "locations_data[0][place_id]": poi["place_id"],
            "locations_data[0][state]": poi["state"],
            "locations_data[0][state_short]": poi["state_short"],
            "locations_data[0][zoom]": poi["zoom"],
            "locations_data[0][distance]": "0",
            "locations_data[0][post_id]": poi["post_id"],
            "selected_brand": "false",
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        store_response = session.post(post_url, data=formdata, headers=headers)
        store_dom = etree.HTML(store_response.text)

        store_url = store_dom.xpath(
            '//li[@itemtype="http://schema.org/LocalBusiness"]//h5[@itemprop="name"]/a/@href'
        )[0]

        hdr = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        }
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        new_street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        if new_street_address:
            street_address = new_street_address[0]
        phone = store_dom.xpath('//div[@itemprop="telephone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = store_dom.xpath("//li/@itemtype")[0].split("/")[-1]
        hours_of_operation = store_dom.xpath(
            '//div[@itemprop="openingHours"]/span/text()'
        )
        hours_of_operation = [e.strip() for e in hours_of_operation if e.strip()]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        location_name = store_dom.xpath('//h5[@itemprop="name"]/a/text()')
        location_name = (
            location_name[0].strip().split(",")[0] if location_name else "<MISSING>"
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
