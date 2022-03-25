# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/lexus/si/sl/drive/14.554764/46.094821?count=10&extraCountries=Sl&limitSearchDistance=0&isCurrentLocation=false&services=",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/lexus/fi/fi/drive/22.898266/62.773976?count=10&extraCountries=&isCurrentLocation=false",
    ]
    domain = "lexus.si"
    for start_url in start_urls:
        data = session.get(start_url).json()
        for poi in data["dealers"]:
            loc_response = session.get(poi["url"])
            hoo = ""
            if loc_response.status_code == 200:
                loc_dom = etree.HTML(loc_response.text)
                hoo = loc_dom.xpath(
                    '//p[strong[contains(text(), "SALON LEXUS")]]/text()'
                )
                if not hoo:
                    hoo = loc_dom.xpath(
                        '//h3[label[contains(text(), "Uudet autot")]]/following-sibling::ul//text()'
                    )
                hoo = [e.strip() for e in hoo if ": od" in e]
                hoo = " ".join(hoo) if hoo else ""
                if not hoo:
                    hoo = loc_dom.xpath(
                        '//h3[label[contains(text(), "Uudet autot")]]/following-sibling::ul//text()'
                    )
                    hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["url"],
                location_name=poi["name"],
                street_address=poi["address"]["address1"].replace(
                    " (lokacija BTC)", ""
                ),
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
