import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "honest-1.com"
    start_url = "https://www.honest-1.com/api/json/places/get"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)
    for poi in data["places"]["locations"]:
        page_url = poi["contacts"]["url"]
        loc_response = session.get(page_url, headers=hdr)
        city = poi["postalAddress"]["city"]
        hoo = ""
        if loc_response.status_code == 200:
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath('//div[@class="header-worktime"]//text()')
            if not hoo:
                hoo = loc_dom.xpath('//span[contains(text(), "am -")]/text()')[:2]
            hoo = " ".join(hoo) if hoo else ""
            city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')
            city = city[0] if city else poi["postalAddress"]["city"]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["entry"]["title"],
            street_address=poi["postalAddress"]["street"],
            city=city,
            state=poi["postalAddress"]["region"],
            zip_postal=poi["postalAddress"]["code"],
            country_code=poi["postalAddress"]["country"],
            store_number="",
            phone=poi["contacts"]["phone"],
            location_type="",
            latitude=poi["geoLocation"]["lat"],
            longitude=poi["geoLocation"]["lng"],
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
