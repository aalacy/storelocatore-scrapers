from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    domain = "eegees.com"
    start_url = "https://eegees.com/locations/"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "View Location")]/@href')
    for page_url in all_locations:
        with SgFirefox() as driver:
            driver.get(page_url)
            loc_dom = etree.HTML(driver.page_source)
        location_name = loc_dom.xpath('//h1/span[@class="heading"]/text()')[0]
        raw_adr = loc_dom.xpath(
            '//h2[contains(text(), "Address")]/following-sibling::p/text()'
        )
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        geo = (
            loc_dom.xpath('//a[contains(@href, "maps?ll")]/@href')[0]
            .split("ll=")[-1]
            .split("&")[0]
            .split(",")
        )
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Lobby Hours")]/following-sibling::p/text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_adr[0],
            city=raw_adr[-1].split(", ")[0],
            state=raw_adr[-1].split(", ")[-1].split()[0],
            zip_postal=raw_adr[-1].split(", ")[-1].split()[-1],
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
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
