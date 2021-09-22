from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "katespade.com"
    start_url = "https://www.katespade.co.uk/on/demandware.store/Sites-ksEuUk-Site/en_GB/Stores-GetNearestStores?latitude=51.5073509&longitude=-0.1277583&countryCode=ES&distanceUnit=mi&maxdistance=5000"

    data = session.get(start_url).json()
    for store_number, poi in data["stores"].items():
        store_url = "https://www.katespade.com" + poi["storeURL"]
        location_name = poi["name"]
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        city = poi["city"]
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["countryCode"]
        phone = poi["phone"]
        location_type = poi["storeType"]
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = etree.HTML(poi["storeHours"]).xpath(
            '//p[contains(text(), "our store is open")]/text()'
        )[1:]
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
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
