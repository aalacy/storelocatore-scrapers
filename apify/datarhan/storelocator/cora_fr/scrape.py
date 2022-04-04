# -*- coding: utf-8 -*-
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.cora.fr/infos-et-services/les-magasins-cora/liste-des-magasins-cora-en-france"
    domain = "cora.fr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(@href, "/magasins/")]/@href')
    response = session.get("https://cora-france.fr/about/liste-des-magasins/")
    dom = etree.HTML(response.text)
    all_locations += dom.xpath('//li/strong/a[@class="has-text-primary"]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)

        poi = loc_dom.xpath('//script[@data-n-head="ssr"]/text()')[-1]
        poi = json.loads(poi)[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=" ".join(poi["address"]["streetAddress"].split()),
            city=poi["address"]["addressLocality"],
            state="",
            zip_postal=poi["address"]["postalCode"],
            country_code=poi["address"]["addressCountry"],
            store_number="",
            phone=poi["telephone"],
            location_type=poi["@type"],
            latitude=poi["geo"]["latitude"],
            longitude=poi["geo"]["longitude"],
            hours_of_operation=poi["openingHours"],
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
