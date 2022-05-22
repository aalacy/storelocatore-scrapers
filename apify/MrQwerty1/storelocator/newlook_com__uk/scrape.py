from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        expected_search_radius_miles=5,
        country_codes=[SearchableCountries.BRITAIN, SearchableCountries.IRELAND],
    )
    for lat, lng in search:
        params = {
            "countryCode": search.current_country().upper(),
            "latitude": str(lat),
            "longitude": str(lng),
        }
        r = session.get(api, headers=headers, params=params)
        js = r.json()["data"]["results"]

        for j in js:
            location_name = j.get("displayName") or ""
            message = j.get("exceptionalMessage") or ""
            if "closed" in location_name.lower() or "closed" in message.lower():
                continue

            a = j.get("address") or {}
            raw_address = a.get("formattedAddress")
            adr1 = a.get("line1") or ""
            adr2 = a.get("line2") or ""
            street_address = f"{adr1} {adr2}".strip()
            city = a.get("town") or ""
            if "," in city:
                city = city.split(",")[0].strip()

            postal = a.get("postalCode")
            try:
                country_code = a["country"]["isocode"]
            except:
                country_code = search.current_country().upper()
            store_number = j.get("name")
            slug = j.get("url")
            page_url = f"https://www.newlook.com{slug}"
            phone = a.get("phone")

            g = j.get("geoPoint") or {}
            latitude = g.get("latitude")
            longitude = g.get("longitude")

            _tmp = []
            try:
                hours = j["openingHours"]["weekDayOpeningList"]
            except KeyError:
                hours = []

            for h in hours:
                day = h.get("weekDay")
                if h.get("closed"):
                    _tmp.append(f"{day}: Closed")
                    continue

                start = h["openingTime"]["formattedHour"]
                end = h["closingTime"]["formattedHour"]
                _tmp.append(f"{day}: {start}-{end}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                raw_address=raw_address,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.newlook.com/"
    api = "https://www.newlook.com/row/json/store-finder/getStores.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
