from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(coords, sgw):
    lat, lng = coords
    for i in range(1, 57):
        api_url = f"https://public-api.hussle.com/search/gyms?filter[default][location_coords]={lat},{lng}&page[default][number]={i}&filter[default][location_distance]=50"
        r = session.get(api_url)
        js = r.json()["data"][0]["data"]["data"]

        for j in js:
            location_type = SgRecord.MISSING
            location_name = j.get("name")
            slug = j.get("b2c_gym_url")
            page_url = f"https://www.hussle.com{slug}"
            phone = j.get("telephone")
            country_code = "GB"
            store_number = j.get("id")

            a = j.get("location") or {}
            street_address = a.get("street_address")
            city = a.get("locality")
            postal = a.get("postcode")
            latitude = a.get("latitude")
            longitude = a.get("longitude")

            _tmp = []
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            hours = j.get("opening_times") or []
            for d, t in zip(days, hours):
                try:

                    t = t["data"]
                    if not t:
                        _tmp.append(f"{d}: Closed")
                        break

                    start = t[0].get("opens_at")
                    close = t[0].get("closes_at")
                    _tmp.append(f"{d}: {start} - {close}")

                except Exception:
                    pass

            hours_of_operation = ";".join(_tmp)

            if j.get("is_temporarily_closed"):
                location_type = "Temporarily Closed"

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                store_number=store_number,
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 18:
            break


if __name__ == "__main__":
    locator_domain = "https://www.hussle.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        countries = [SearchableCountries.BRITAIN]
        search = DynamicGeoSearch(
            country_codes=countries, expected_search_radius_miles=50
        )
        for coord in search:
            fetch_data(coord, writer)
