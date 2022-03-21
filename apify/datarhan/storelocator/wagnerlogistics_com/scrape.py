import re
from lxml import etree
from time import sleep
from pyjsparser import PyJsParser

from sgrequests import SgRequests
from sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.wagnerlogistics.com/who-we-are/operations-map"
    domain = "wagnerlogistics.com"

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
        location_name = poi[5][0][1][0].strip()
        street_address = ""
        city = ""
        state = ""
        zip_code = ""
        phone = ""
        addr_raw = ""
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
            addr_raw = addr[0] if addr else raw_data
            addr = parse_address_intl(addr_raw)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
        phone = re.findall(r"\d\d\d-\d\d\d-\d\d\d\d", raw_data)
        phone = phone[0] if phone else ""
        latitude = poi[1][0][0][0]
        longitude = poi[1][0][0][1]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation="",
            raw_address=addr_raw,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
