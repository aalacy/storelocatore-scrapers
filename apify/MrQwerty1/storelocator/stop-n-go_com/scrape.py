from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for lat, lng in search:
        api = f"https://www.kwiktrip.com/locproxy.php?Latitude={lat}&Longitude={lng}&maxDistance=100&limit=250"
        r = session.get(api, headers=headers)
        js = r.json()["stores"]

        for j in js:
            location_name = j.get("name").strip()
            a = j.get("address") or {}
            street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
            city = a.get("city")
            state = a.get("state")
            postal = a.get("zip")

            store_number = j.get("id")
            page_url = f"https://www.kwiktrip.com/locator/store?id={store_number}"
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            _tmp = []
            hours = j.get("hours") or []
            for h in hours:
                day = h.get("dayOfWeek")
                start = h.get("openTime")
                close = h.get("closeTime")

                if start != close:
                    _tmp.append(f"{day}: {start} - {close}")
                else:
                    _tmp.append(f"{day}: Closed")

            hours_of_operation = ";".join(_tmp)
            is24 = j.get("open24Hours")
            if is24:
                hours_of_operation = "Open 24 Hours"

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.kwiktrip.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
