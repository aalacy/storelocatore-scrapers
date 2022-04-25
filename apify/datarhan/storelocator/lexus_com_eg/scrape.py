from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://www.lexus.com.eg/api/v1/getCenters?location={}"
    domain = "lexus.com.eg"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.EGYPT], expected_search_radius_miles=500
    )
    for code in all_codes:
        data = session.get(start_url.format(code), headers=hdr).json()

        for poi in data["data"]:
            raw_address = poi["address"]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.lexus.com.eg/forms/find-a-center",
                location_name=poi["name"],
                street_address=street_address,
                city=addr.city,
                state="",
                zip_postal=addr.postcode,
                country_code="EG",
                store_number=poi["id"],
                phone=poi["phone"],
                location_type=", ".join(poi["type"]),
                latitude=poi["lat"],
                longitude=poi["long"],
                hours_of_operation="",
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
