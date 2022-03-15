from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.sephora.ro/on/demandware.store/Sites-Sephora_RO-Site/ro_RO/Stores-FindNearestStores?latitude={}&longitude={}&storeservices="
    domain = "sephora.ro"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.ROMANIA], expected_search_radius_miles=50
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr).json()
        for poi in response["locations"]:
            hoo = []
            for e in poi["schedule"]:
                hoo.append(f'{e["Day"]} {e["Time"]}')
            hoo = " ".join(hoo)
            phone = poi["phone"]
            if phone == "0040":
                phone = ""

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["url"],
                location_name=poi["name"],
                street_address=poi["address1"],
                city=poi["city"],
                state="",
                zip_postal=poi["postal"],
                country_code=poi["country_code"],
                store_number=poi["id"],
                phone=phone,
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
