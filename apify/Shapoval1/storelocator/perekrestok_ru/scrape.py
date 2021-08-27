from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.perekrestok.ru"
    api_url = "https://www.perekrestok.ru/api/customer/1.4.1.0/shop/points"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Auth": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzUxMiJ9.eyJpYXQiOjE2Mjk5ODk2MjQsImV4cCI6MTYzMDAxODQyNCwiZCI6IjEuNC4xLjA6YzBkNTlkYWQtMmMxMS00MzRlLWJjNWUtZjMzZTMwN2ZlOGI2IiwianRpIjoiZGI3NTY4NWEtODUzNC00ZWI0LWI2ZTMtMDc0NTMzMTBjMDBhIiwiaXAiOiIxNzIuMjAuOS4xMjYiLCJ1IjoiODA5MmZiNWMtZjI1OC00ODY1LWE4MDAtMDcwMmFlN2Y1OTQyIn0.ABTQwswKZifA0MVbfq_oBEJmctjKqd8yPfCakQkvMVJd8QwbYydJ18SD_hBMN2INifg23EGgICZF3g51SENVxodaAb8_uM2p_0S3OGODBzhF9cHr6ens1h1nknBf3Zm0G4YfTJ8q_rvcUI71D-7V76xXglvganQ6I5MbGiZqCDbu7KYI",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "If-None-Match": '"4251853ab95c5307045c0154150b2b9f"',
        "Cache-Control": "max-age=0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["content"]["items"]
    for j in js:
        ids = j.get("id")
        page_url = "https://www.perekrestok.ru/shops"
        session = SgRequests()
        r = session.get(
            f"https://www.perekrestok.ru/api/customer/1.4.1.0/shop/{ids}",
            headers=headers,
        )
        js = r.json()["content"]

        location_name = js.get("title")
        street_address = (
            "".join(js.get("address")).replace("\r\n", " ").replace("\n", " ")
        )
        country_code = "RU"
        city = "".join(js.get("city").get("name"))
        store_number = j.get("id")
        latitude = js.get("location").get("coordinates")[0]
        longitude = js.get("location").get("coordinates")[1]
        if latitude == "0":
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = js.get("schedule")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
