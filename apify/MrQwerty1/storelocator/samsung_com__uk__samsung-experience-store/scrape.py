from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://papi.gethatch.com/locations/5c88b7e546e0fb000143fc7c/geo/list"
    data = '{"countryCode":"GB","geoCenterArea":{"center":{"latitude":"51.5112139","longitude":"-0.1198244"},"distance":500000},"filters":[{"columnName":"storeTypes","operation":"equal","value":["1_ses"]}]}'
    page_url = "https://www.samsung.com/uk/samsung-experience-store/locations/"
    r = session.post(api, data=data, headers=headers)
    js = r.json()["locations"]

    for j in js:
        location_name = j.get("name")
        a = j.get("address") or {}
        street_address = a.get("street")
        city = j.get("locality")
        postal = a.get("zip")
        phone = j.get("telephone")
        store_number = j.get("id")
        c = j.get("coordinates") or {}
        latitude = c.get("latitude")
        longitude = c.get("longitude")
        hours_of_operation = j.get("openingHours")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://samsung.com/uk/samsung-experience-store/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.samsung.com/",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Access-Control-Allow-Origin": "*",
        "Origin": "https://www.samsung.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
        "Pragma": "no-cache",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
