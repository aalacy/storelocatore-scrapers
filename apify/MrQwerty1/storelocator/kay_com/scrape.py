from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def fetch_data(_zip, sgw: SgWriter):
    for i in range(777):
        api = f"https://www.kay.com/store-finder/find?q={_zip}&page={i}&includeKayStores=true&includeKayOutletStores=true"

        try:
            r = session.get(api, headers=headers)
            js = r.json().get("data") or []
        except:
            break

        for j in js:
            location_name = j.get("displayName")
            location_type = "Kay Jewelers"
            slug = j.get("url")
            page_url = f"https://www.kay.com{slug}"
            if "/null" in page_url:
                page_url = SgRecord.MISSING
            street_address = f'{j.get("line1")} {j.get("line2") or ""}'.strip()
            city = j.get("town")
            state = j.get("regionIsoCodeShort")
            postal = j.get("postalCode")
            country_code = "US"
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            store_number = j.get("name")
            _type = j.get("baseStore") or ""
            if _type == "kayoutlet":
                location_type = "Kay Jewelers Outlet"

            _tmp = []
            items = j.get("openings") or {}
            for k, v in items.items():
                _tmp.append(f"{k} {v}")

            hours_of_operation = ";".join(_tmp)
            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 5:
            break


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.kay.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for _z in DynamicZipSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
        ):
            fetch_data(_z, writer)
