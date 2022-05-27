from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://location.coinsource.net/location/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://coinsource.net",
        "Connection": "keep-alive",
        "Referer": "https://coinsource.net/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["data"]:
        a = j.get("location")
        location_name = j.get("name") or "<MISSING>"
        if (
            location_name == "Warehouse Gemini Tester 2"
            or location_name == "ATM Bitcoin"
            or location_name == "Crypto Coin"
        ):
            continue
        location_type = j.get("atmType")
        country_code = a.get("country") or "US"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        street_address = (
            "".join(a.get("street")).replace("null", "").strip() or "<MISSING>"
        )
        city = "".join(a.get("city")).strip() or "<MISSING>"
        state = "".join(a.get("state")).strip() or "<MISSING>"
        postal = "".join(a.get("zip")).strip() or "<MISSING>"
        if postal == "TX":
            postal = "<MISSING>"
        store_number = j.get("id")
        page_url = f"https://coinsource.net/bitcoin-atm-locations?kiosk={store_number}"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://coinsource.net"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
