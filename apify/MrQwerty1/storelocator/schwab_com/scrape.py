from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=40
    )
    for lat, lng in search:

        api = f"https://client.schwab.com/public/branchlocator/Locator.ashx?lat={lat}&lang={lng}&brnchtype=undefined"
        r = session.get(api, headers=headers)
        js = r.json()["BranchesOutForMap"]
        if js is None:
            continue

        for j in js:
            street_address = j.get("BranchAddr") or ""
            if "coming" in street_address.lower():
                continue
            city = j.get("City")
            state = j.get("State")
            postal = j.get("Zipcode")
            country_code = "US"
            store_number = j.get("BranchID")
            location_name = j.get("BranchName")
            page_url = f"https://client.schwab.com/public/branchlocator/branchdetails.aspx?branchid={store_number}"
            location_type = j.get("Type")
            phone = j.get("GeneralAppointmentPhone")
            latitude = j.get("Latitude")
            longitude = j.get("Longitude")

            _tmp = []
            hours = j.get("WeeklyBranchTimes") or []
            for h in hours:
                day = h.get("Day")
                start = h.get("Open")
                end = h.get("Close")
                _tmp.append(f"{day}: {start}-{end}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                location_type=location_type,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.schwab.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
