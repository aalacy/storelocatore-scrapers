from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    start_url = "https://stores.mooresclothing.ca/modules/multilocation/?near_location={}&services__in=&language_code=en-us&published=1&within_business=true"
    domain = "mooresclothing.ca"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=200
    )
    for code in all_codes:
        try:
            data = session.get(start_url.format(code)).json()
        except Exception:
            continue
        all_locations = data["objects"]
        for poi in all_locations:
            hoo = []
            for e in poi["formatted_hours"]["primary"]["grouped_days"]:
                hoo.append(f'{e["label"]} {e["content"]}')
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["location_url"],
                location_name=poi["custom_fields"]["store_name"],
                street_address=poi["street"],
                city=poi["city"],
                state=poi["state_name"],
                zip_postal=poi["postal_code"],
                country_code=poi["country"],
                store_number=poi["id"],
                phone=poi["phones"][0]["number"],
                location_type="",
                latitude=poi["lat"],
                longitude=poi["lon"],
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
