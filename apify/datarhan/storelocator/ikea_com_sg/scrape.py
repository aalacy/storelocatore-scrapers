from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.ikea.com/sg/en/stores/"
    domain = "ikea.com/sg"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//section[div[div[h2[contains(text(), "IKEA")]]]]')[1:]
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_data = poi_html.xpath(
            './/following-sibling::section[1]//a[contains(@href, "daddr=")]/@href'
        )
        street_address = location_name.replace("IKEA ", "")
        latitude = ""
        longitude = ""
        if raw_data:
            geo = (
                poi_html.xpath(".//following-sibling::section[1]//a/@href")[0]
                .split("@")[-1]
                .split(",")
            )
            raw_data = (
                poi_html.xpath(
                    './/following-sibling::section[1]//a[contains(@href, "daddr=")]/@href'
                )[0]
                .split("addr=")[-1]
                .split("@")[0]
                .split("+")
            )
            addr = parse_address_intl(" ".join(raw_data[2:]))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            latitude = geo[0]
            longitude = geo[1]
            city = addr.city
            zip_code = addr.postcode
        phone = poi_html.xpath(
            './/following-sibling::section[1]//a[contains(@href, "tel")]/text()'
        )
        phone = phone[0] if phone else ""
        hoo = poi_html.xpath(
            './/h3[strong[contains(text(), "STORE OPENING HOURS")]]/following-sibling::p[1]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="SG",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
