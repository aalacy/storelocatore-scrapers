from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://www.nbtbank.com/locations/index.html"
    api = "https://www.nbtbank.com/locations/locations.json"
    r = session.get(api, headers=headers)
    js = r.json()["features"]

    for j in js:
        geo = j.get("geometry", {}).get("coordinates") or [
            SgRecord.MISSING,
            SgRecord.MISSING,
        ]
        j = j.get("properties")
        location_name = j.get("name")
        if location_name.find("ATM") != -1:
            continue
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        phone = j.get("phone")
        latitude = geo[1]
        longitude = geo[0]

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
        for d in days:
            if d == "Tuesday":
                part = "Tues"
            elif d == "Thursday":
                part = "Thurs"
            else:
                part = d[:3]

            time = j.get(f"Lobby_{part}") or "Closed"
            _tmp.append(f"{d}: {time}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.nbtbank.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "If-Modified-Since": "Fri, 19 Nov 2021 11:17:57 GMT",
        "If-None-Match": 'W/"0x8D9AB4E3D952DB8"',
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
