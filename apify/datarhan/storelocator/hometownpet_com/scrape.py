from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "hometownpet.com"
    start_url = "https://cdn.shopify.com/s/files/1/0812/3573/t/111/assets/sca.storelocatordata.json"

    all_locations = session.get(start_url).json()
    for poi in all_locations:
        hoo = ""
        if poi.get("schedule"):
            hoo = etree.HTML(poi["schedule"]).xpath("//text()")
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.petsense.com/pages/store-locator",
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["postal"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
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
