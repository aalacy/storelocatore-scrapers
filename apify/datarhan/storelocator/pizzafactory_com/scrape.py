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

    domain = "pizzafactory.com"
    start_url = "https://www.pizzafactory.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(@id, "search_result")]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')[0]
        poi = json.loads(poi)

        hoo = []
        for e in poi["openingHoursSpecification"]:
            if type(e["dayOfWeek"]) == list:
                for day in e["dayOfWeek"]:
                    hoo.append(f'{day} {e["opens"]} - {e["closes"]}')
            else:
                hoo.append(f'{e["dayOfWeek"]} {e["opens"]} - {e["closes"]}')
        hours_of_operation = " ".join(hoo) if hoo else SgRecord.MISSING

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["name"],
            street_address=poi["address"]["streetAddress"],
            city=poi["address"]["addressLocality"],
            state=poi["address"]["addressRegion"],
            zip_postal=poi["address"]["postalCode"],
            country_code=poi["address"]["addressCountry"],
            store_number=SgRecord.MISSING,
            phone=poi["telephone"],
            location_type=poi["@type"],
            latitude=poi["geo"]["latitude"],
            longitude=poi["geo"]["longitude"],
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
