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

    start_url = "https://www.carespot.com/wp-admin/admin-ajax.php"
    domain = "medpost.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {"action": "locations-get_map_locations"}
    response = session.post(start_url, headers=hdr, data=frm)
    data = json.loads(response.text)

    all_locations = data["data"]
    for poi in all_locations:
        poi_html = etree.HTML(poi["info"])
        store_url = poi_html.xpath("//div[@data-post_id]/a/@href")[0]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        if loc_dom.xpath('//p[contains(text(), "Coming Soon!")]'):
            continue
        raw_address = loc_dom.xpath('//p[@itemprop="address"]/text()')
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//div[@class="location-street-address"]/text()'
            )
        raw_address = [e.strip() for e in raw_address if e.strip() and e.strip() != ","]

        location_name = poi["title"]
        location_name = (
            location_name.replace("&amp;", "&").replace("&#8211;", "-")
            if location_name
            else "<MISSING>"
        )
        street_address = poi_html.xpath('//span[@itemprop="streetAddress"]//text()')
        street_address = [e.strip() for e in street_address if e.strip()]
        if not street_address:
            street_address = raw_address[:1]
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        city = poi_html.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0].strip() if city else "<MISSING>"
        if city == "<MISSING>":
            city = raw_address[-1].split(", ")[0]
        state = poi_html.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0].strip() if state else "<MISSING>"
        if state == "<MISSING>":
            state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = poi_html.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        if zip_code == "<MISSING>":
            zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi_html.xpath('//a[contains(@href, "tel")]//text()')
        phone = [e.strip() for e in phone if e.strip()]
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        hoo = loc_dom.xpath('//div[@class="hours"]/p//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        if not hoo:
            hoo = loc_dom.xpath('//div[@id="hours"]/div/ul[1]/li//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
