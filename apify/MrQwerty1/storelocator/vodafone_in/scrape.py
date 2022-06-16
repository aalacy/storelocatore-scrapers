import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def get_street(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()

    return street


def fetch_data(sgw: SgWriter):
    api = "https://www.myvi.in/bin/getStoreLocations"
    search = DynamicGeoSearch(
        expected_search_radius_miles=50, country_codes=[SearchableCountries.INDIA]
    )

    for lat, lng in search:
        params = {
            "userlat": str(lat),
            "userlong": str(lng),
        }
        r = session.get(api, headers=headers, params=params)
        text = r.json()["DXLSTOREDETAILS"]
        js = json.loads(text)["storelist"]

        for j in js:
            raw_address = j.get("oldAddressFreeText")
            a = j.get("address") or {}

            street_address = get_street(raw_address)
            city = a.get("locality")
            postal = a.get("postalCode")
            state = a.get("subLocality")
            country_code = "IN"
            store_number = j.get("code")
            location_name = j.get("name")
            phone = j.get("primaryPhone")

            try:
                g = j["geographicLocation"]["coordinates"][0]
            except:
                g = {}
            latitude = g.get("latitude")
            longitude = g.get("longitude")

            _tmp = []
            hours = j.get("calendar") or []
            for h in hours:
                day = h.get("day") or ""
                if "Special" in day:
                    continue
                inter = h.get("workingHours")
                _tmp.append(f"{day}: {inter}")

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
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://vodafone.in/"
    page_url = "https://www.myvi.in/help-support/store-locator"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
