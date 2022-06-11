from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.dsquared2.com/storelocator"
    domain = "dsquared2.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    data = session.get(
        "https://www.dsquared2.com/on/demandware.store/Sites-dsquared2-row-Site/en_US/Stores-FindStores?showMap=false&radius=50000&lat=35.6803997&long=139.7690174",
        headers=hdr,
    ).json()
    for poi in data["stores"]:
        hoo = poi.get("storeHours")
        if hoo:
            hoo = " ".join(hoo.split())

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=" ".join(poi["address1"].split()),
            city=poi["city"],
            state=poi["stateCode"],
            zip_postal=poi["postalCode"],
            country_code=poi["countryCode"],
            store_number=poi["ID"],
            phone="",
            location_type=poi["shopType"],
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
