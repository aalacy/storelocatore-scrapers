from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def fetch_data(_zip, sgw: SgWriter):
    for i in range(777):
        api = f"https://www.zales.com/store-finder?q={_zip}&page={i}"

        r = session.get(api, headers=headers)
        try:
            js = r.json().get("data") or []
        except:
            return

        for j in js:
            _type = j.get("baseStore") or ""
            location_name = "Zales"
            location_type = "Zales"
            slug = j.get("url")
            page_url = f"https://www.zales.com{slug}?baseStore={_type}"
            if page_url.endswith("/null"):
                page_url = SgRecord.MISSING

            street_address = f'{j.get("line1")} {j.get("line2") or ""}'.strip()
            city = j.get("town")
            state = j.get("region")
            postal = j.get("postalCode")
            country_code = "US"
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            store_number = j.get("name")
            if _type == "zalesoutlet":
                location_name = "Zales Outlet"
                location_type = "Outlet"

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
    locator_domain = "https://www.zales.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.zales.com/store-finder",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for _z in DynamicZipSearch(
            country_codes=[SearchableCountries.USA],
            max_search_distance_miles=100,
            expected_search_radius_miles=20,
        ):
            fetch_data(_z, writer)
