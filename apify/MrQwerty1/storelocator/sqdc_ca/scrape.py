from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    data = '{"zoomLevel":3,"mapBounds":{"southWest":{"lat":20.103234596275197,"lng":-173.92398705},"northEast":{"lat":62.33218935413471,"lng":29.98226294999999}},"isSearch":false,"pageSize":900}'
    api = "https://www.sqdc.ca/api/storelocator/markers"
    r = session.post(api, headers=headers, data=data)
    js = r.json()["Stores"]

    for j in js:
        location_name = j.get("Name")
        slug = j.get("Url") or ""
        page_url = f"https://www.sqdc.ca{slug}"
        a = j.get("Address") or {}
        street_address = f'{a.get("Line1")} {a.get("Line2") or ""}'.strip()
        city = a.get("City")
        state = a.get("RegionName")
        postal = a.get("PostalCode")
        country = a.get("CountryCode")
        phone = a.get("PhoneNumber")
        latitude = a.get("Latitude")
        longitude = a.get("Longitude")
        store_number = j.get("Number")

        _tmp = []
        try:
            hours = j["Schedule"]["OpeningHours"]
        except:
            hours = []

        for h in hours:
            day = h.get("LocalizedDay")
            if h.get("IsClosed"):
                _tmp.append(f"{day}: Closed")
                continue

            try:
                times = h.get("OpeningTimes")[0]
            except:
                times = {}

            start = times.get("BeginTime")
            end = times.get("EndTime")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.sqdc.ca/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-CA",
        "Referer": "https://www.sqdc.ca/en-CA/Stores",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.sqdc.ca",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    session = SgRequests(proxy_country="ca")
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
