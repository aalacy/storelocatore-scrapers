import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.illegalpetes.com/Locations/du"
    domain = "illegalpetes.com"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
    data = json.loads(data)
    for poi in data["props"]["pageProps"]["locations"]:
        page_url = "https://www.illegalpetes.com/Locations/" + poi["fields"]["linkName"]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath(
            '//h3[contains(text(), "Main Store Hours")]/following-sibling::div[@class="location-hours"]/text()'
        )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h3[text()="Hours"]/following-sibling::div[@class="location-hours"]/text()'
            )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h3[text()="Main Hours"]/following-sibling::div[@class="location-hours"]/text()'
            )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h3[text()="Main Store hours"]/following-sibling::div[@class="location-hours"]/text()'
            )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h3[text()="Colfax Hours"]/following-sibling::div[@class="location-hours"]/text()'
            )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h3[contains(text(), "Hours")]/following-sibling::div[@class="location-hours"]/text()'
            )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["fields"]["storeName"],
            street_address=poi["fields"]["locationInfo"]["fields"]["addressLine1"],
            city=poi["fields"]["locationInfo"]["fields"]["city"],
            state=poi["fields"]["locationInfo"]["fields"]["state"],
            zip_postal=poi["fields"]["locationInfo"]["fields"]["zip"],
            country_code="",
            store_number="",
            phone=poi["fields"]["storePhone"],
            location_type="",
            latitude=poi["fields"]["locationInfo"]["fields"]["latLong"]["lat"],
            longitude=poi["fields"]["locationInfo"]["fields"]["latLong"]["lon"],
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
