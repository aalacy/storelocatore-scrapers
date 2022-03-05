import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://columbia-sportswear.ro/magazine/"
    domain = "columbia-sportswear.ro"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_geo = re.findall(r"points.push\((.+?)\);", response.text.replace("\n", ""))
    all_geo = [demjson.decode(e) for e in all_geo]

    all_locations = dom.xpath('//h2[@class="shop-name"]/a/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath(
            '//section[@class="col-sm-5 shop-data"]//h1[@class="shop-title"]//text()'
        )

        location_name = "".join(location_name)
        raw_address = loc_dom.xpath(
            '//td[strong[contains(text(), "Bolt címe:")]]/following-sibling::td[1]/text()'
        )
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//td[strong[contains(text(), "Adresa magazinului")]]/following-sibling::td[1]/text()'
            )
        raw_address = raw_address[0]
        addr = parse_address_intl(raw_address)
        phone = loc_dom.xpath(
            '//td[strong[contains(text(), "Telefonszám:")]]/following-sibling::td[1]/text()'
        )
        if not phone:
            phone = loc_dom.xpath(
                '//td[strong[contains(text(), "Număr de telefon:")]]/following-sibling::td[1]/text()'
            )
        phone = phone[0]
        for e in all_geo:
            if e["name"] == location_name:
                latitude = e["y"]
                longitude = e["x"]
        hoo = loc_dom.xpath(
            '//div[@class="shop-data-openings shop-data-table"]/p/text()'
        )
        hoo = " ".join(" ".join(hoo).split())
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="RO",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
            raw_address=raw_address,
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
