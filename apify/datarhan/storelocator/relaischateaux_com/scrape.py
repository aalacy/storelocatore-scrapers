import re
import csv
import json
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.relaischateaux.com/gb/update-destination-results"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    areas = ["83", "13"]
    for area in areas:
        frm = {"page": "1", "areaId": area}
        hdr = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        response = session.post(start_url, data=frm, headers=hdr)
        data = json.loads(response.text)
        dom = etree.HTML(data["html"])
        all_locations = dom.xpath('//div[@itemtype="//schema.org/Hotel"]')
        next_page = dom.xpath('//a[contains(text(), "next")]/@href')
        while next_page:
            page = next_page[0].split("=")[-1]
            frm["page"] = page
            response = session.post(start_url, data=frm, headers=hdr)
            data = json.loads(response.text)
            dom = etree.HTML(data["html"])
            all_locations += dom.xpath('//div[@itemtype="//schema.org/Hotel"]')
            next_page = dom.xpath('//a[contains(text(), "next")]/@href')

        for poi_html in all_locations:
            store_url = poi_html.xpath('.//a[span[@itemprop="name"]]/@href')[0]
            if "mexico/" in store_url:
                continue
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = poi_html.xpath('.//span[@itemprop="name"]/text()')
            location_name = location_name[0] if location_name else "<MISSING>"
            street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
            street_address = (
                street_address[0].strip() if street_address else "<MISSING>"
            )
            city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
            city = city[0] if city else "<MISSING>"
            state = loc_dom.xpath(
                '//span[@itemprop="postalCode"]/following-sibling::span[1][not(@itemprop)]/text()'
            )
            state = state[0].replace(",", "") if state else "<MISSING>"
            zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
            zip_code = zip_code[0].replace(",", "") if zip_code else "<MISSING>"
            country_code = loc_dom.xpath('//span[@itemprop="addressCountry"]/text()')
            country_code = country_code[0] if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath('//span[@itemprop="telephone"]/a/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "Hotel"
            latitude = loc_dom.xpath("//@data-lat")
            latitude = latitude[0] if latitude else "<MISSING>"
            longitude = loc_dom.xpath("//@data-lng")
            longitude = longitude[0] if longitude else "<MISSING>"
            hours_of_operation = "<MISSING>"

            item = [
                domain,
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
