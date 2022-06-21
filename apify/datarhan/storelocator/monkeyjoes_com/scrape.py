from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "moneymart.com"
    start_url = "https://www.monkeyjoes.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//h3[@class="blue mb-1"]/a/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h3[@class="blue mb-1"]/text()')[0]
        raw_data = loc_dom.xpath(
            '//div[@class="location-info"]//p[@class="mb-1"]/text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if len(raw_data) == 3:
            raw_data = [", ".join(raw_data[:2])] + raw_data[2:]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        hoo = loc_dom.xpath('//p[strong[contains(text(), "HOURS")]]/text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        geo = (
            loc_dom.xpath("//iframe/@src")[-1]
            .split("!2d")[1]
            .split("!2m3")[0]
            .split("!3d")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_data[0],
            city=raw_data[1].split(",")[0],
            state=raw_data[1].split(",")[1].split()[0],
            zip_postal=raw_data[1].split(",")[1].split()[1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1],
            longitude=geo[0],
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
