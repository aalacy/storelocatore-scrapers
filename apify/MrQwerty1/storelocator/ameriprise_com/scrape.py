from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def fetch_data(_zip, sgw):
    for i in range(0, 10000, 10):
        criteria = (
            "{"
            + f'"searchTerm":"{_zip}","sortExpression":null,"numberOfRowsToReturn":10,"startRowIndex":{i},"radialDistance":50,"defaultRadius":0,"areasOfFocus":[],"designations":[],"linkedIn":false,"latitude":0,"longitude":0,"searchType":"zip code"'
            + "}"
        )
        data = {"criteria": criteria}

        r = session.post(
            "https://www.ameripriseadvisors.com/webservices/advisorSearch.aspx",
            data=data,
        )
        js = r.json()["advisorModels"]

        for j in js:
            location_type = j.get("advisorType")
            if location_type != "Private Wealth Advisor":
                location_type = "Team"

            location_name = j.get("displayName") or ""
            location_name = location_name.replace("&amp;", "&").replace("&#39;", "'")
            slug = j.get("advisorURL")
            page_url = f"https://www.ameripriseadvisors.com{slug}/contact/"
            country_code = "US"

            locations = j.get("locations") or []
            for loc in locations:
                phone = loc.get("phone")
                store_number = loc.get("locationId")
                street_address = (
                    f'{loc.get("address1")} {loc.get("address2") or ""}'.strip()
                )
                city = loc.get("city")
                state = loc.get("state")
                postal = loc.get("postal")
                latitude = loc.get("lat")
                longitude = loc.get("lon")

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
                hours = loc.get("locationOfficeHours") or []
                for h in hours:
                    enabled = h.get("enabled")
                    index = h.get("dayOfWeek")
                    day = days[index - 1]
                    if not enabled:
                        _tmp.append(f"{day}: Closed")
                        continue
                    start = h.get("startTime") or ""
                    end = h.get("endTime") or ""
                    line = f"{day}: {start}-{end}".replace("01/01/1970 ", "")
                    _tmp.append(line)

                hours_of_operation = ";".join(_tmp)

                row = SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
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

        if len(js) < 10:
            break


if __name__ == "__main__":
    locator_domain = "https://www.ameriprise.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        countries = [SearchableCountries.USA]
        search = DynamicZipSearch(
            country_codes=countries, expected_search_radius_miles=25
        )
        for _zip in search:
            fetch_data(_zip, writer)
