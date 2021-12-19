import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://www.skipton.co.uk/branchfinder/branches"
    domain = "skipton.co.uk"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//ul[@id="branchesList"]//a/text()')
    for location_name in all_locations:
        page_url = f'https://www.skipton.co.uk/branchfinder/{location_name.replace(" ", "%20")}'
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath("//address/text()")
        raw_address = [e.strip() for e in raw_address if e.strip()]
        if len(raw_address) == 5:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        if len(raw_address) == 4:
            state = raw_address[2]
            zip_code = raw_address[3]
        else:
            state = ""
            zip_code = raw_address[2]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        geo = loc_dom.xpath('//input[@id="jsonData"]/@value')[0]
        geo = json.loads(geo)
        hoo = []
        hoo = loc_dom.xpath('//div[@class="opening-times"]/dl//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0]["BranchLatitude"],
            longitude=geo[0]["BranchLongitude"],
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
