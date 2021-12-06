from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://www.onitsukatiger.com/on/demandware.store/Sites-asics-us-Site/en_US/Stores-GetNearestStores?latitude=41.3873974&longitude=2.168568&countryCode=ES&distanceUnit=km&maxdistance=50000&brands=&isDisableCheckRTI=true",
        "https://www.onitsukatiger.com/on/demandware.store/Sites-asics-eu-Site/en_EU/Stores-GetNearestStores?latitude=41.3873974&longitude=2.168568&countryCode=DE&distanceUnit=km&maxdistance=50000&brands=&isDisableCheckRTI=true",
        "https://www.onitsukatiger.com/on/demandware.store/Sites-asics-au-Site/en_AU/Stores-GetNearestStores?latitude=-33.8688197&longitude=151.2092955&countryCode=AU&distanceUnit=km&maxdistance=50000&brands=&isDisableCheckRTI=true",
    ]
    domain = "onitsukatiger.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for url in start_urls:
        data = session.get(url, headers=hdr).json()
        for store_number, poi in data["stores"].items():
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]
            hoo = ""
            if poi["storeHours"]:
                hoo = etree.HTML(poi["storeHours"]).xpath("//text()")
                hoo = " ".join([e.strip() for e in hoo if e.strip()])
            state = poi["stateCode"]
            if state and state.isdigit():
                state = ""

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["storeUrl"],
                location_name=poi["name"],
                street_address=street_address,
                city=poi["city"],
                state=state,
                zip_postal=poi["postalCode"],
                country_code=poi["countryCode"],
                store_number=store_number,
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
