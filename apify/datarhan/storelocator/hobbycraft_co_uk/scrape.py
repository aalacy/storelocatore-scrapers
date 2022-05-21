import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "hobbycraft.co.uk"
    start_url = "https://www.hobbycraft.co.uk/storelist/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//div[@class="b-storelocator_locations-item_location"]/a/@href'
    )

    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        poi = loc_dom.xpath("//@data-stores-model")[0]
        poi = json.loads(poi)
        poi = poi["stores"][0]
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        hoo = []
        for e in poi["openingHours"]:
            hoo.append(f'{e["displayName"]}: {e["startTime"]} - {e["endTime"]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state="",
            zip_postal=poi["postalCode"],
            country_code="UK",
            store_number=poi["ID"],
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
