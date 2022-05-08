import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "nautica.com"
    start_url = "https://www.nautica.com/on/demandware.store/Sites-nau-Site/default/Stores-AllStores"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_regions = dom.xpath('//div[@class="listname"]/a/@href')
    for url in list(set(all_regions)):
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//a[@class="store-item"]/@href')
        for page_url in all_locations:
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')[0]
            poi = json.loads(poi)
            hoo = loc_dom.xpath('//div[@class="storehours"]/p/text()')
            hoo = " ".join(hoo)
            if "this is not goodbye" in hoo.lower():
                continue
            state = poi["address"]["addressRegion"]
            state = state if state != "null" else ""
            zip_code = poi["address"]["postalCode"]
            zip_code = zip_code if zip_code != "null" else ""
            phone = poi["telephone"]
            phone = phone.split("&")[0] if phone != "null" else ""
            street_address = poi["address"]["streetAddress"]
            if street_address and street_address.endswith(","):
                street_address = street_address[:-1]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=street_address,
                city=poi["address"]["addressLocality"],
                state=state,
                zip_postal=zip_code,
                country_code=poi["address"]["addressCountry"],
                store_number=poi["@id"].split("=")[-1],
                phone=phone,
                location_type=poi["@type"],
                latitude=poi["geo"]["latitude"],
                longitude=poi["geo"]["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
