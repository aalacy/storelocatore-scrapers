# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://cobblestone.com/?sm-xml-search=1&lat=35.4376935&lng=-109.09931&radius=0&namequery=35.4483771%2C%20-109.085354&query_type=all&limit=0&sm_category&locname&address&city&state&zip&pid=260"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        page_url = poi["url"]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        street_address = poi["address"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        phone = poi["phone"]
        if not phone:
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/strong/text()')
            phone = phone[0] if phone else ""
        coming_soon = loc_dom.xpath('//h2/strong[contains(text(), "COMING SOON!")]')
        if coming_soon:
            continue
        hoo = loc_dom.xpath('//div[@class="location__hours"]/dl//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["post_title"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=poi["ID"],
            phone=phone,
            location_type=SgRecord.MISSING,
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
