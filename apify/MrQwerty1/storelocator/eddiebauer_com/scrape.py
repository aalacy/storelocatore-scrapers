import base64
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    countries = [SearchableCountries.USA, SearchableCountries.CANADA]
    search = DynamicGeoSearch(country_codes=countries, expected_search_radius_miles=100)

    for lat, lng in search:
        api = "https://eddiebauer.radius8.com/api/v1/streams/stores"
        dog = f"Authorization=R8-Gateway%20App%3Dr8connect%2C%20key%3D4k2wIG8pFMUXvQnpRNmnAq%2C%20Type%3DSameOrigin&X-Domain-Id=eddiebauer&Geo-Position={lat}%3B{lng}&X-Device-Id=ed088a8e-9e1e-87df-7384-211fc4bec533&X-Request-Tag=y0tM5YEFa%2BLsmddayuPbMp0D53RweI1JnrmbrZwulBkScijcRyGbfpcmrYx1xwPMtmovs24BDty2A2xXCm9zrCXkm%2FfyFS23WScCw0yBICA%3D%23NDE5MTUz&"
        hdog = base64.b64encode(dog.encode("utf8")).decode("utf8")
        params = (("lat", lat), ("radius", "200"), ("lng", lng), ("hdog", hdog))
        r = session.get(api, headers=headers, params=params)
        js = r.json()["results"]
        print((lat, lng), ":", len(js))

        for j in js:
            location_name = j.get("name") or ""
            if location_name.find("not real") != -1:
                continue
            if "outlet" in location_name.lower():
                location_name = "Eddie Bauer Outlet"
            else:
                location_name = "Eddie Bauer"

            a = j.get("address") or {}
            street_address = f'{a.get("address1")} {a.get("address2") or ""}'.strip()
            city = a.get("city")
            state = a.get("state")
            postal = a.get("postal_code") or ""
            if len(postal) == 4:
                postal = f"0{postal}"

            country = a.get("country")
            if country == "USA":
                country_code = "US"
            else:
                country_code = "CA"

            store_number = j.get("store_code")
            phone = j.get("contact_info", {}).get("phone")
            g = j.get("geo_point", {}) or {}
            latitude = g.get("lat")
            longitude = g.get("lng")

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
            h = j.get("hours", {}) or {}

            for d in days:
                key = d[:3].lower()
                start = h[key][0]
                close = h[key][1]

                if start.lower().find("closed") != -1:
                    _tmp.append(f"{d}: Closed")
                else:
                    _tmp.append(
                        f"{d}: {start[:2]}:{start[2:]} - {close[:2]}:{close[2:]}"
                    )

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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.eddiebauer.com/"
    page_url = "https://www.eddiebauer.com/store-locator"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://www.eddiebauer.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
