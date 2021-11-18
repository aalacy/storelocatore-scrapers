import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.uniformdestination.com/find-a-store/"
    domain = "uniformdestination.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[@id="simple-locator-all-js-extra"]/text()')[0]
        .split("wpsl_locator_all =")[-1]
        .replace(";\n/* ]]> */\n", "")
    )
    data = json.loads(data)

    for poi in data["locations"]:
        page_url = poi["permalink"]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = loc_dom.xpath('//div[@class="wpsl-location-address"]/p/text()')
        phone = loc_dom.xpath('//div[@class="wpsl-location-phone"]/p/text()')
        phone = phone[0].split("Phone: ")[-1] if phone else ""
        hoo = loc_dom.xpath(
            '//div[@class="wpsl-location-info"]/following-sibling::p/text()'
        )
        if not hoo:
            hoo = loc_dom.xpath('//div[@class="wpsl-location-additionalinfo"]/p/text()')
        hoo = (
            " ".join(
                [
                    e.replace("\r\n", " ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                    for e in hoo
                    if e.strip() and "Note: " not in e
                ]
            )
            .replace("Hours of Operation", "")
            .replace("Hours of operation:", "")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["title"],
            street_address=raw_address[0],
            city=raw_address[-1].split(", ")[0],
            state=raw_address[-1].split(", ")[-1].split()[0],
            zip_postal=raw_address[-1].split(", ")[-1].split()[-1],
            country_code="",
            store_number=poi["id"],
            phone=phone,
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
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
