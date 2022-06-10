import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    api = "https://iapi.kernelatm.com/v1/machines"
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    for lat, lng in search:
        data = {"latitude": lat, "longitude": lng}
        r = session.post(api, headers=headers, data=json.dumps(data))
        js = r.json()["data"]

        for j in js:
            j = j.get("location") or {}
            location_name = j.get("business_name")
            street_address = j.get("address")
            city = j.get("city")
            state = j.get("state")
            postal = j.get("postal_code")
            country = j.get("country")

            phone = j.get("phone_number")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            meta = j.get("metadata") or {}
            location_type = meta.get("store_type")
            store_number = j.get("location_id")

            _tmp = []
            hours = j.get("hours") or {}

            for day, h in hours.items():
                if not h:
                    _tmp.append("Closed")
                    break
                start = h.get("open") or ""
                end = h.get("close") or ""
                if start == end:
                    _tmp.append(f"{day}: 24 hours")
                else:
                    start = start.split("T")[1].split(":00-")[0]
                    end = end.split("T")[1].split(":00-")[0]
                    _tmp.append(f"{day}: {start}-{end}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country,
                location_type=location_type,
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://kernelatm.com/"
    page_url = "https://kernelatm.com/find-atm"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Origin": "https://kernelatm.com",
        "Connection": "keep-alive",
        "Referer": "https://kernelatm.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
