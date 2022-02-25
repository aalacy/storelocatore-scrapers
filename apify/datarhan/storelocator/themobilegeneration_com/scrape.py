import ssl
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    start_url = "https://themobilegeneration.com/locations/"
    domain = "themobilegeneration.com"
    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//tr[contains(@class, "wpgmaps_mlist_row")]')
        for poi_html in all_locations:
            raw_data = poi_html.xpath(".//td/text()")
            raw_address = raw_data[1].split(",")
            phone = poi_html.xpath('./td/p[strong[contains(text(), "Phone")]]/text()')
            phone = phone[0] if phone else ""
            hoo = poi_html.xpath('./td/p[strong[contains(text(), "Hours:")]]/text()')
            hoo = " ".join(hoo)
            zip_code = ""
            if len(raw_address[2].split()) == 2:
                zip_code = raw_address[2].split()[1]

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=raw_data[0],
                street_address=raw_address[0],
                city=raw_address[1],
                state=raw_address[2].split()[0],
                zip_postal=zip_code,
                country_code=raw_address[-1],
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
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
