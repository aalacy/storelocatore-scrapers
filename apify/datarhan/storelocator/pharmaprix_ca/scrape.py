from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "pharmaprix.ca"
    start_url = "https://www1.pharmaprix.ca/sdmapi/store/getnearbystoresbyminmax?lang=fr-QC&lat={}&lng={}&minLat={}&minLng={}&maxLat={}&maxLng={}"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
        "X-NewRelic-ID": "UwEFUF5XGwQHUFJUDwY=",
    }

    all_codes = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=20
    )
    for lat, lng in all_codes:
        all_locations = session.get(
            start_url.format(lat, lng, lat - 0.2, lng - 0.25, lat + 0.2, lng + 0.25),
            headers=headers,
        ).json()
        for poi in all_locations:
            hoo = ""
            if poi.get("WeekDays"):
                hoo = list(
                    map(lambda d, h: d + " " + h, poi["WeekDays"], poi["StoreHours"])
                )
                hoo = " ".join(hoo) if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=f"https://www1.pharmaprix.ca/fr/store-locator/store/{poi['StoreID']}",
                location_name=poi["Name"],
                street_address=poi["Address"],
                city=poi["City"],
                state=poi["Province"]["Abbreviation"],
                zip_postal=poi["PostalCode"],
                country_code="CA",
                store_number=poi["StoreID"],
                phone=poi["Telephone"],
                location_type="",
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
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
