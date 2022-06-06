# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.drycleanusa.mx/sucursales/"
    domain = "drycleanusa.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath("//figure/a/@href")
    for url in all_states[1:]:
        s_url = urljoin(start_url, url)
        response = session.get(s_url)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//a[@data-action="button"]/@href')
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            raw_address = loc_dom.xpath('//div[@class="j-module n j-text "]/p//text()')
            if not raw_address:
                raw_address = loc_dom.xpath(
                    '//p[@style="text-align: center;"]/span/text()'
                )
            raw_address = [e.strip() for e in raw_address if e.strip()][0]
            location_name = loc_dom.xpath("//h2/text()")[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            state = s_url.split("/")[-2].replace("-", " ").capitalize()
            zip_code = addr.postcode
            if zip_code:
                zip_code = zip_code.replace("C.P", "").replace(".", "")
            hoo = loc_dom.xpath(
                '//div[h3[contains(text(), "Horarios de Servicio")]]/following-sibling::div[1]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=state,
                zip_postal=zip_code,
                country_code="MX",
                store_number="",
                phone="",
                location_type="",
                latitude="",
                longitude="",
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
