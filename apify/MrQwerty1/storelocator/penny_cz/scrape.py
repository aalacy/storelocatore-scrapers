from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.penny.cz/api/stores"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = "Penny"
        street_address = j.get("street")
        city = j.get("city")
        postal = j.get("zip")
        country_code = "CZ"
        store_number = j.get("storeId")
        phone = j.get("phone")
        g = j.get("coordinate") or {}
        latitude = g.get("x")
        longitude = g.get("y")

        _tmp = []
        hours = j.get("openingTimes") or []
        for h in hours:
            day = h.get("dayOfWeek")
            inter = "-".join(h.get("times") or [])
            _tmp.append(f"{day}: {inter}")

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
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.penny.cz/"
    page_url = "https://www.penny.cz/prodejny"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "correlationid": "f353f7da-4879-48e5-8059-53c5dc8d821d-1651558750091",
        "Connection": "keep-alive",
        "Referer": "https://www.pennymarket.cz/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
