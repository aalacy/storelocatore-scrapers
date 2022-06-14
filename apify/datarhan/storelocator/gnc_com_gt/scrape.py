from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://gnc.com.gt/pages/nuestras-tiendas-1"
    domain = "gnc.com.gt"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//article[@class="item-content"]/div/div[p[strong]]')
    all_locations += dom.xpath(
        '//article[@class="item-content"]/div[@data-icon="gpicon-textblock"]/div[p[b]]'
    )
    all_locations += dom.xpath(
        '//article[@class="item-content"]/div[@data-icon="gpicon-textblock"]/div[p[span[@style="font-weight: 700; letter-spacing: 0.3px;"]]]'
    )
    all_locations += dom.xpath(
        '//article[@class="item-content"]/div[@data-icon="gpicon-textblock"]/div[p[span[strong]]]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//strong/text()")
        if not location_name:
            location_name = poi_html.xpath(".//b/text()")
        if not location_name:
            location_name = poi_html.xpath(".//p/span/strong/text()")
        location_name = " ".join([e.strip() for e in location_name if e.strip()])
        raw_address = poi_html.xpath(".//p/span/text()")
        if not raw_address:
            raw_address = poi_html.xpath(".//div/p/b/text()")[1:-1]
        raw_address += poi_html.xpath(".//p/text()")
        if not raw_address and "C.C. PLAZA MADERO CARR. A EL SALVADOR" in location_name:
            raw_address = location_name.split(" A EL SALVADOR")[-1].split("Tel.")[:1]
            location_name = "C.C. PLAZA MADERO CARR. A EL SALVADOR"
        raw_address = [e.strip() for e in raw_address if e.strip() and "Tel." not in e]
        raw_address = " ".join(raw_address)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath('.//*[contains(text(), "Tel.")]/text()')
        phone = phone[0].replace("Tel.", "").split("/")[0] if phone else ""
        if phone == "Pendiente":
            phone = ""
        if not location_name and "conchas" in raw_address.lower():
            location_name = "LAS CONCHAS"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
            raw_address=raw_address,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
