import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=30
    )
    for lat, lng in search:
        data = {
            "search": "",
            "radius": "100mi",
            "isAcceptingNewPatients": True,
            "latitude": str(lat),
            "longitude": str(lng),
            "network": "Everett",
        }
        r = session.post(api, headers=headers, data=json.dumps(data))
        try:
            js = r.json()["result"]["data"]["providers"]
            js = js.get("hits") or []
        except:
            js = []

        for j in js:
            j = j["provider"]
            try:
                loc = j["locations"][0]
            except:
                loc = dict()

            a = loc.get("addressInfo")
            store_number = j.get("individualProviderId")
            page_url = f"https://www.everettclinic.com/locations-nav/locations/-/-/{store_number}.html"
            try:
                location_name = j["providerInfo"]["businessName"]
            except KeyError:
                continue

            street_address = a.get("line1")
            city = a.get("city")
            state = a.get("state")
            postal = a.get("zip")
            country_code = "US"
            phone = loc.get("telephoneNumbers")[0].get("telephoneNumber")
            latitude, longitude = a.get("lat_lon").split(",")

            _types = []
            types = loc.get("plans")[0].get("specialties")[0].get("enrollment") or []
            for t in types:
                _t = t.get("enrollmentRole") or ""
                _types.append(_t)

            location_type = ";".join(_types)

            _tmp = []
            hours = loc.get("hoursOfOperation") or []
            for h in hours:
                day = h.get("dayOfWeek").replace("One", "")
                start = h.get("fromHour")
                close = h.get("toHour")
                _tmp.append(f"{day}: {start} - {close}")

            hours_of_operation = ";".join(_tmp) or "<MISSING>"
            if hours_of_operation != "<MISSING>":
                days = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                for d in days:
                    if d not in hours_of_operation:
                        hours_of_operation += f";{d}: Closed"

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
                location_type=location_type,
                phone=phone,
                store_number=store_number,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.everettclinic.com/"
    api = "https://www.everettclinic.com/bin/optumcare/findlocations"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "CSRF-Token": "undefined",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.everettclinic.com",
        "Referer": "https://www.everettclinic.com/provider-lookup/search-results.html?isAcceptingNewPatients=false&search=%2098373&latitude=47.1474103&longitude=-122.3239889&network=Everett",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
