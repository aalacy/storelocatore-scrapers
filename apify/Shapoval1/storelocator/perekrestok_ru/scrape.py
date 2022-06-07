from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.perekrestok.ru"
    api_url = "https://www.perekrestok.ru/api/customer/1.4.1.0/shop/points"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Auth": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzUxMiJ9.eyJpYXQiOjE2NDQ0MTM3NTMsImV4cCI6MTY0NDQ0MjU1MywiZCI6IjEuNC4xLjA6MzU4MDFjNDAtM2VhZS00YThkLTlkMjQtZDllNDkzOGY1OTdjIiwianRpIjoiYTc0NjM4YTUtMmY5Yi00MWU1LWJjOWUtYWM4Mjc1YjY5YjQzIiwiaXAiOiI5My43OC4yMTIuMTY4IiwidSI6ImZjM2ZmMWVhLTMwYmMtNGNhMC1hM2Q4LTMwNTU3ZTQxYjA2YyJ9.AVxLN0XZ3suzz4dtaOR0xTeEF-g4y4r1ApEIviXX-YudfL1CACLizieH4hJ6_7E1Scj6mlY2udSf43pCTfiyO0NOAMOZfz6XisiGesO018m_2yPcEhAMHcvjLSqJH-YBDztRqtbLiStAcXkncQqPUogirz2dRBVN8Z6XBvIszPmSsyKU",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["content"]["items"]
    for j in js:
        ids = j.get("id")

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
        page_url = f"https://www.perekrestok.ru/shops/shop/{ids}"
        city = "".join(js.get("city").get("name"))
        store_number = j.get("id")
        latitude = js.get("location").get("coordinates")[1]
        longitude = js.get("location").get("coordinates")[0]
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
