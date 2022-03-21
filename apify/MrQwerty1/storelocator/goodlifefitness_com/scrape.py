from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(lat, lng, sgw: SgWriter):
    lat, lng = str(lat).replace(".", "_"), str(lng).replace(".", "_")
    url = f"https://www.goodlifefitness.com/content/goodlife/en/clubs/jcr:content/root/responsivegrid/responsivegrid_1015243366/findaclub.ClubByMapBounds.{lat}.{lng}.undef.undef.2022127.json"
    r = session.get(url)
    js = r.json()["map"]["response"]

    for j in js:
        location_name = j.get("ClubName")
        a = j.get("Address") or {}
        street_address = a.get("Address1")
        city = a.get("City")
        state = a.get("Province")
        postal = a.get("PostalCode")
        country_code = a.get("Country")
        phone = j.get("Phone")
        c = j.get("Coordinate") or {}
        latitude = c.get("Latitude")
        longitude = c.get("Longitude")
        page_url = j.get("pagePath")
        store_number = j.get("ClubNumber")

        _tmp = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        hours = j.get("OperatingHours") or []

        for h in hours:
            day = days[h.get("Day") - 1]
            start = h.get("StartTime").split("T")[1][:-3]
            end = h.get("EndTime").split("T")[1][:-3]
            _tmp.append(f"{day.capitalize()}: {start} - {end}")

        hours_of_operation = ";".join(_tmp)
        if j.get("Is247"):
            hours_of_operation = "Mon - Sun: 24h"
        if not j.get("IsOpen"):
            hours_of_operation = "Closed"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.goodlifefitness.com/"
    session = SgRequests()

    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=10
        )
        for la, ln in search:
            fetch_data(la, ln, writer)
