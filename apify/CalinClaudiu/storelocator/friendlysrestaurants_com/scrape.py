from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=RYTHVSEODZRALZIS&center=37.27094681255562,-95.95631851752042&coordinates=11.36576814158218,-62.852159129670014,63.17612548352906,-129.06047790537082&multi_account=false&page=1&pageSize=100",
        "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=RYTHVSEODZRALZIS&center=37.27094681255562,-95.95631851752042&coordinates=11.36576814158218,-62.852159129670014,63.17612548352906,-129.06047790537082&multi_account=false&page=2&pageSize=100",
    ]

    domain = "friendlysrestaurants.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        all_locations = session.get(start_url, headers=hdr).json()
        for poi in all_locations:
            page_url = "https://locations.friendlysrestaurants.com" + poi["llp_url"]
            poi = poi["store_info"]
            hoo = ""
            if page_url.strip():
                with SgFirefox() as driver:
                    driver.get(page_url)
                    sleep(5)
                    loc_dom = etree.HTML(driver.page_source)
                hoo = loc_dom.xpath('//dl[@itemprop="openingHours"]//text()')
                hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["address"],
                city=poi["locality"],
                state=poi["region"],
                zip_postal=poi["postcode"],
                country_code=poi["country"],
                store_number="",
                phone=poi["phone"],
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
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
