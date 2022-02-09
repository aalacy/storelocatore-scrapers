# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://crazybowlsandwraps.com/?sm-xml-search=1&lat=38.6268404&lng=-90.1993389&radius=0&namequery=38.6270025, -90.1994042&query_type=all&limit=0&hours=&sm_category=&sm_tag=&locname=&address=&city=&state=&zip=&pid=37"
    domain = "crazybowlsandwraps.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        page_url = poi["url"]
        if "coming soon" in poi["name"]:
            continue

        hoo = ""
        if page_url:
            with SgFirefox() as driver:
                driver.get(page_url)
                loc_dom = etree.HTML(driver.page_source)
            hoo = loc_dom.xpath('//div[@class="hours"]/div/text()')
            hoo = ", ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["url"],
            location_name=poi["name"].replace("&#8217;", "'"),
            street_address=poi["address"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=poi["ID"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
