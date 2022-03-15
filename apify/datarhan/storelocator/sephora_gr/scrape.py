from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.sephora.gr/on/demandware.store/Sites-Sephora_RO-Site/el_GR/Stores-FindNearestStores?latitude={}&longitude={}&storeservices="
    domain = "sephora.gr"

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.GREECE], expected_search_radius_miles=20
    )
    for lat, lng in all_coords:
        data = session.get(start_url.format(lat, lng)).json()
        for poi in data["locations"]:
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]
            if poi["address3"]:
                street_address += ", " + poi["address3"]
            hoo = []
            for e in poi["schedule"]:
                hoo.append(f'{e["Day"]} {e["Time"]}')
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["url"],
                location_name=poi["name"],
                street_address=street_address,
                city=poi["city"],
                state="",
                zip_postal=poi["postal"],
                country_code=poi["country_code"],
                store_number=poi["id"],
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
