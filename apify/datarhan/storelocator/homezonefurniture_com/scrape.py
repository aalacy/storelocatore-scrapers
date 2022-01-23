from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://homezonefurniture.com/en/allshops"
    domain = "homezonefurniture.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "Read More")]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_adr = loc_dom.xpath(
            '//strong[contains(text(), "Address:")]/following-sibling::span[1]/span/text()'
        )
        phone = loc_dom.xpath(
            '//strong[contains(text(), "Phone:")]/following-sibling::span/text()'
        )
        if not phone:
            continue
        phone = phone[0].strip()
        hoo = loc_dom.xpath('//div[@id="store-locator-open_hour"]//td/text()')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_adr[0],
            city=raw_adr[-1].split(", ")[0],
            state=" ".join(raw_adr[-1].split(", ")[-1].split()[:-1]),
            zip_postal=raw_adr[-1].split(", ")[-1].split()[-1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=loc_dom.xpath("//@data-latitude")[0],
            longitude=loc_dom.xpath("//@data-longitude")[0],
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
