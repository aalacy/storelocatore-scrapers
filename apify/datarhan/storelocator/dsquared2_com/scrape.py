from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.dsquared2.com/experience/es/?yoox_storelocator_action=true&action=yoox_storelocator_get_all_stores"
    domain = "dsquared2.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        location_type = ""
        if poi.get("store-type"):
            location_type = ", ".join([e["name"] for e in poi["store-type"]])
        raw_address = poi.get("wpcf-yoox-store-geolocation-address")
        if not raw_address:
            raw_address = poi.get("wpcf-yoox-store-address")
        if not raw_address:
            continue
        raw_address = " ".join(raw_address.split())
        city = ""
        zip_code = poi.get("wpcf-yoox-store-zip")
        if poi.get("location"):
            city = poi["location"].get("city", {}).get("name")
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        if not city:
            city = addr.city
        if not zip_code:
            zip_code = addr.postcode
        state = addr.state
        if state and 'M3' in state:
            state = ""
        hoo = poi.get("wpcf-yoox-store-hours")
        if hoo:
            hoo = " ".join(hoo.split())

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["permalink"],
            location_name=poi["post_title"],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=poi["wpcf-yoox-store-country-iso"],
            store_number=poi["ID"],
            phone=poi.get("wpcf-yoox-store-phone"),
            location_type=location_type,
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
            raw_address=raw_address,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
