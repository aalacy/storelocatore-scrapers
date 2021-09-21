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

    start_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=RYTHVSEODZRALZIS&center=39.56720202057154,-76.633608738563&coordinates=38.22052657072621,-75.0131253401254,40.88822245379342,-78.25409213700041&multi_account=false&page=1&pageSize=50"
    domain = "friendlysrestaurants.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        poi = poi["store_info"]
        page_url = poi["website"]
        hoo = ""
        if page_url.strip():
            with SgFirefox() as driver:
                driver.get(page_url)
                sleep(10)
                loc_dom = etree.HTML(driver.page_source)
            hoo = loc_dom.xpath('//dl[@itemprop="openingHours"]/@content')
            hoo = hoo[0] if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["website"],
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
