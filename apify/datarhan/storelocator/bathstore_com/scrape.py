# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.bathstore.com/stores"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "initialStockists")]/text()')[0]
        .split("initialStockists =")[-1]
        .strip()
    )

    all_locations = json.loads(data)
    for poi in all_locations:
        page_url = f'https://www.bathstore.com/stores/{poi["alias"]}'
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//div[@class="stockist-hours"]//table//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo)
        city = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        if city:
            city = city[0].strip()
        if not city:
            city = (
                loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')[0]
                .split(",")[1]
                .strip()
            )
        if city.endswith(","):
            city = city[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"]["address1"],
            city=city,
            state=SgRecord.MISSING,
            zip_postal=poi["address"]["postcode"],
            country_code=SgRecord.MISSING,
            store_number=poi["id"],
            phone=poi["telephone"],
            location_type=SgRecord.MISSING,
            latitude=poi["location"]["lat"],
            longitude=poi["location"]["lng"],
            hours_of_operation=hours_of_operation,
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
