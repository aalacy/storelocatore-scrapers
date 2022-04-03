from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api = "https://www.gbarbosa.com.br/api/dataentities/LJ/search/?_fields=storeName,address,complement,city,state,businessHours,phone,storeType,storeLink,zipCode,city,state"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zipCode")
        country_code = "BR"
        location_name = j.get("storeName")
        phone = j.get("phone")
        location_type = j.get("storeType")

        text = j.get("storeLink") or ""
        try:
            latitude, longitude = text.split("/@")[1].split(",")[:2]
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        hours_of_operation = j.get("businessHours") or ""
        hours_of_operation = hours_of_operation.replace(" | ", ";").replace(" |", "")

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
            location_type=location_type,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.gbarbosa.com.br/"
    page_url = "https://www.gbarbosa.com.br/lojas"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.gbarbosa.com.br/lojas",
        "REST-Range": "resources=0-500",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
