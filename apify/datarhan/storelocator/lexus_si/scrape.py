# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/lexus/si/sl/drive/14.554764/46.094821?count=10&extraCountries=Sl&limitSearchDistance=0&isCurrentLocation=false&services="
    domain = "lexus.si"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    data = session.get(start_url, headers=hdr).json()
    for poi in data["dealers"]:
        loc_response = session.get(poi["url"])
        loc_dom = etree.HTML(loc_response.text)
        raw_data = loc_dom.xpath('//p[b[contains(text(), "SALON LEXUS")]]/text()')
        raw_data = " ".join([e.strip() for e in raw_data if e.strip()])
        hoo = raw_data.split("as salona")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["url"],
            location_name=poi["name"],
            street_address=poi["address"]["address1"],
            city=poi["address"]["city"],
            state=poi["address"]["region"],
            zip_postal=poi["address"]["zip"],
            country_code=poi["country"],
            store_number=poi["localDealerID"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["address"]["geo"]["lat"],
            longitude=poi["address"]["geo"]["lon"],
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
