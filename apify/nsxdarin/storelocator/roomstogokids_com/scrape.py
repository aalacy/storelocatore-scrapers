from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.roomstogo.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.roomstogo.com/stores",
        "Proxy-Authorization": "Basic ZG1pdHJpeTIyc2hhcGFAZ21haWwuY29tOnJxeFN6YzI0NnNzdnByVVZwdHJT",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    r = session.get(
        "https://www.roomstogo.com/page-data/stores/page-data.json", headers=headers
    )
    js = r.json()["result"]["pageContext"]["stores"]["stores"]
    for j in js:
        slug = j.get("slug")
        page_url = f"https://www.roomstogo.com{slug}"
        location_name = j.get("StoreName") or "<MISSING>"
        location_type = j.get("StoreType") or "<MISSING>"
        street_address = f"{j.get('Address1')} {j.get('Address2') or ''}".replace(
            "None", ""
        ).strip()
        state = j.get("State") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = j.get("City") or "<MISSING>"
        store_number = j.get("StoreNumber") or "<MISSING>"
        latitude = j.get("Location").get("latLng").get("lat") or "<MISSING>"
        longitude = j.get("Location").get("latLng").get("lng") or "<MISSING>"
        phone = j.get("PhoneNumber") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        hours = j.get("StoreHours")
        tmp = []
        if hours:
            for d in days:
                day = str(d).capitalize()
                opens = hours.get(f"{d}Open")
                closes = hours.get(f"{d}Closed")
                line = f"{day} {opens} - {closes}"
                if opens == closes:
                    line = f"{day} Closed"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
