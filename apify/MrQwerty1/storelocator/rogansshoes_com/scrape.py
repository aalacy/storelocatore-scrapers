from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://apistage.rogansshoes.com/rspublishproduct/GetStoreLocationsDetails/ALL/undefined"
    params = (("state", "ALL"),)

    r = session.get(api, headers=headers, params=params)
    js = r.json()["StoreLocations"]

    for j in js:
        a = j.get("StoreAddress") or ""
        street_address = j.get("Addressline1")
        city = a.split(",")[0].strip()
        state, postal = a.split(",")[1].split()
        country_code = "US"
        store_number = j.get("WarehouseId")
        slug = j.get("seourl")
        page_url = f"https://www.rogansshoes.com/{slug}"
        location_name = j.get("StoreName")
        phone = j.get("PhoneNumber")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        hours_of_operation = j.get("StoreTiming")

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
    locator_domain = "https://www.rogansshoes.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.rogansshoes.com/",
        "Authorization": "Basic YXBpc3RhZ2Uucm9nYW5zc2hvZXMuY29tfDhhOGI0OTMxLTdkNTctNDJlOC1hMDA1LWIxYzBjY2U0OWYxZA==",
        "Origin": "https://www.rogansshoes.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
