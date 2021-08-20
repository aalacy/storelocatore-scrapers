import re
import csv
from lxml import etree
from time import sleep
from pyjsparser import PyJsParser

from sgrequests import SgRequests
from sgselenium import SgFirefox
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
    start_url = "https://www.wagnerlogistics.com/who-we-are/operations-map"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    parser = PyJsParser()
    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(20)
        dom = etree.HTML(driver.page_source)
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
    for poi in all_locations:
        store_url = start_url
        location_name = poi[5][0][1][0].strip()
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zip_code = "<MISSING>"
        phone = "<MISSING>"
        if poi[5][1]:
            raw_data = (
                poi[5][1][1][0]
                .strip()
                .replace("\xa0", ", ")
                .replace("\n", ", ")
                .split(", ")
            )
            raw_data = [e.strip() for e in raw_data if e.strip()]
            raw_data = ", ".join(raw_data)
            addr = re.findall(r"(.+) \d\d\d-", raw_data)
            addr = addr[0] if addr else raw_data
            addr = parse_address_intl(addr)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
        phone = re.findall(r"\d\d\d-\d\d\d-\d\d\d\d", raw_data)
        phone = phone[0] if phone else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi[1][0][0][0]
        longitude = poi[1][0][0][1]
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
