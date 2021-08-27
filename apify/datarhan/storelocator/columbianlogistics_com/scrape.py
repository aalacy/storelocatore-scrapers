import re
import csv
from lxml import etree
from pyjsparser import PyJsParser

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
    items = []

    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
    start_url = "https://www.columbianlogistics.com/warehousing/3pl-warehousing/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    parser = PyJsParser()
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_poi = dom.xpath('//div[@class="right-list"]/p/strong')
    map_id = dom.xpath("//iframe/@src")[0].split("mid=")[-1].split("&z")[0]
    response = session.get("https://www.google.com/maps/d/edit?hl=ja&mid=" + map_id)
    dom = etree.HTML(response.text)
    script = dom.xpath("//script/text()")[0]
    js = parser.parse(script)
    pagedata = js["body"][1]["declarations"][0]["init"]["value"]

    data = pagedata.replace("true", "True")
    data = data.replace("false", "False")
    data = data.replace("null", "None")
    data = data.replace("\n", "")
    data = eval(data)

    all_locations = data[1][6][0][12][0][13][0]
    for poi_html in all_poi:
        store_url = start_url
        location_name = poi_html.xpath("text()")[0].strip()
        if not location_name:
            continue
        raw_address = poi_html.xpath(".//following::text()")[1]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        phone = "<INACCESSIBLE>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        geo = []
        for poi in all_locations:
            poi_name = poi[5][0][1][0].split("-")[-1].strip()
            if location_name == poi_name:
                geo = poi[1][0][0]
            elif poi_name.split("&")[0] in location_name:
                geo = poi[1][0][0]
            if geo:
                latitude = geo[0]
                longitude = geo[1]
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
