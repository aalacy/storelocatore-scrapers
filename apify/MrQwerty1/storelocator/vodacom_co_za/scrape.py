from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(coords, sgw: SgWriter):
    lat, lng = coords
    api = f"https://www.vodacom.co.za//cloud/rest/v1/geographicSiteManagement/geographicSites?latitude={lat}&longitude={lng}&storeTypes=Chatz&storeTypes=Repair%20Centre&storeTypes=Vodacom%204U&storeTypes=Vodacom%20Approved%20Dealer&storeTypes=Vodacom%20Shop&storeTypes=Vodacom%20Express&clientType=CBU"
    r = session.get(api, headers=headers)
    try:
        js = r.json()["result"]
    except:
        return

    for j in js:
        a = j.get("address") or {}
        try:
            location_type = j["siteType"]["description"]
        except:
            location_type = SgRecord.MISSING
        try:
            g = a["geographicLocation"]["geometry"][0]
        except:
            g = {}

        row = SgRecord(
            page_url=SgRecord.MISSING,
            location_name=j.get("name"),
            street_address=a.get("streetName"),
            city=a.get("locality"),
            state=a.get("state"),
            zip_postal=a.get("postalcode"),
            country_code="ZA",
            store_number=j.get("code"),
            phone=j.get("mainPhone"),
            latitude=g.get("x"),
            longitude=g.get("y"),
            location_type=location_type,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    locator_domain = "https://www.vodacom.co.za/"
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.SOUTH_AFRICA],
        expected_search_radius_miles=50,
    )
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for coord in search:
            fetch_data(coord, writer)
