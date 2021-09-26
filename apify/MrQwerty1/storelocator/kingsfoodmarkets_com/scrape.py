from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://local.kingsfoodmarkets.com/locator"

    r = session.get(api, headers=headers, params=params)
    js = r.json()["response"]["entities"]
    for j in js:
        j = j.get("profile") or {}
        a = j.get("address") or {}

        location_name = f'{j.get("name")} {j.get("geomodifier") or ""}'.strip()
        page_url = j.get("websiteUrl")
        street_address = f'{a.get("line1")} {a.get("line2") or ""}'.strip()
        city = a.get("city")
        state = a.get("region")
        postal = a.get("postalCode")
        country_code = a.get("countryCode")
        try:
            phone = j["mainPhone"]["display"]
        except KeyError:
            phone = SgRecord.MISSING

        latitude = j["yextDisplayCoordinate"]["lat"]
        longitude = j["yextDisplayCoordinate"]["long"]

        _tmp = []
        try:
            hours = j["hours"]["normalHours"]
        except KeyError:
            hours = []

        for h in hours:
            day = h.get("day")
            if h.get("isClosed"):
                _tmp.append(f"{day}: Closed")
            else:
                start = str(h["intervals"][0]["start"])
                end = str(h["intervals"][0]["end"])
                if len(start) == 3:
                    start = f"0{start}"
                _tmp.append(f"{day}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "application/json",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    params = (
        ("country", "US"),
        ("storetype", "5655"),
        ("l", "en"),
    )
    locator_domain = "https://kingsfoodmarkets.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
