import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.newcold.com/sites/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath("""//*[contains(text(), '"places":')]/text()""")[0]
    data = re.findall(r".maps\((.+)\).data", data)[0]
    data = json.loads(data)

    all_locations = data["places"]
    for poi in all_locations:
        store_url = etree.HTML(poi["content"]).xpath("//a/@href")[0]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = loc_dom.xpath('//p[strong[contains(text(), "Address")]]/text()')[
            :2
        ]
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//header[h3[contains(text(), "Address")]]/following-sibling::div[1]/p/text()'
            )[:3]
        raw_address = [e.strip() for e in raw_address if "+" not in e]
        addr = parse_address_intl(" ".join(raw_address))

        location_name = poi["title"]
        street_address = poi["address"]
        city = poi["location"]["city"]
        state = poi["location"].get("state")
        if not state:
            state = addr.state
        state = state if state else "<MISSING>"
        zip_code = poi["location"].get("postal_code")
        if not zip_code:
            zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["location"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        if country_code == "Verenigde Staten":
            country_code = "United States"
        store_number = poi["id"]
        phone = loc_dom.xpath('//div[@class="iconbox_content_container  "]/p[1]/text()')
        phone = [e.strip() for e in phone if e.strip()]
        for e in phone:
            if e.startswith("+"):
                phone = e
                break
        if type(phone) == list:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["lat"]
        longitude = poi["location"]["lng"]
        hoo = loc_dom.xpath('//div[@class="avia-animated-number-content"]/p/text()')
        hours_of_operation = (
            hoo[-1].split(":")[-1].strip().replace("Ouvrir ", "")
            if hoo
            else "<MISSING>"
        )

        if location_name == "NewCold Wakefield":
            zip_code = "WF3 4FE"

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
