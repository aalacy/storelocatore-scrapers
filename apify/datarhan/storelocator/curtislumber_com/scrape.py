from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.curtislumber.com/locations/"
    domain = "curtislumber.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//header/a/@href")
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//nav[@class="crumbs"]/ul/li/text()')[0]
        raw_address = loc_dom.xpath('//div[@class="wpsl-location-address"]/span/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        phone = loc_dom.xpath(
            '//div[@class="location-info"]//a[contains(@href, "tel")]/text()'
        )[0]
        geo = (
            loc_dom.xpath(
                '//div[span[a[contains(text(), "{}")]]]//span[@class="dir-location-directions"]/a/@href'.format(
                    location_name
                )
            )[0]
            .split("=")[-1]
            .split(",")
        )
        hoo = loc_dom.xpath('//div[@class="full hours"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state=raw_address[2],
            zip_postal=raw_address[3],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
