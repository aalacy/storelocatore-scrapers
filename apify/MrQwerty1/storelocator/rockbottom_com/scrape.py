from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://rockbottom.com/locations/getLocationJson"
    r = session.get(api, headers=headers)
    js = r.json()["markers"]

    for j in js:
        slug = j.get("city_slug")
        page_url = f"https://rockbottom.com/locations/{slug}"

        location_name = j.get("city")
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zipcode")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        days = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wednesday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Saturday",
            "7": "Sunday",
        }

        _tmp = []
        hours = j.get("hours") or ""
        for h in hours.split(";"):
            _t = h.split(",")
            day = days.get(_t.pop(0))
            try:
                start, end = _t
                start = f"{start[:2]}:{start[2:]}"
                end = f"{end[:2]}:{end[2:]}"
                _tmp.append(f"{day}: {start}-{end}")
            except:
                pass

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
    locator_domain = "https://rockbottom.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
