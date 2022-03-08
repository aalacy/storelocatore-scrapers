from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://eu.katespade.com/on/demandware.store/Sites-ksEuRoe-Site/en_US/Stores-GetNearestStores?latitude=52.52000659999999&longitude=13.404954&countryCode=&distanceUnit=mi&maxdistance=300000"
    domain = "eu.katespade.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for store_number, poi in all_locations["stores"].items():
        page_url = "https://eu.katespade.com" + poi["storeURL"]
        poi_html = etree.HTML(poi["storeHours"])
        hoo = poi_html.xpath("//p/text()")[2:-1]
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        city = poi["city"]
        if not city:
            addr = parse_address_intl(poi["name"])
            city = addr.city

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=city,
            state=poi["stateCode"],
            zip_postal=poi["postalCode"],
            country_code=poi["countryCode"],
            store_number=store_number,
            phone=poi["phone"],
            location_type=poi["storeType"],
            latitude=poi["latitude"].replace(",", "."),
            longitude=poi["longitude"].replace(",", "."),
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
