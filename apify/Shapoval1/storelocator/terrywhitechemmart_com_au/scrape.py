from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://terrywhitechemmart.com.au/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://terrywhitechemmart.com.au",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    json_data = {"": ""}
    r = session.post(
        "https://terrywhitechemmart.com.au/store-api/get-stores-summary",
        headers=headers,
        json=json_data,
    )
    js = r.json()
    for j in js["data"]:

        storeId = j.get("storeId")
        slug = j.get("storeSlug")
        page_url = f"https://terrywhitechemmart.com.au/stores/{slug}"
        location_name = j.get("storeName") or "<MISSING>"
        street_address = (
            f"{j.get('addressLine1')} {j.get('addressLine2')}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        state = j.get("state") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = "AU"
        city = j.get("suburb") or "<MISSING>"
        store_number = j.get("sharedStoreIdentifier") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Origin": "https://terrywhitechemmart.com.au",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "max-age=0",
            "TE": "trailers",
        }

        json_data = {
            "storeId": f"{storeId}",
        }

        r = session.post(
            "https://terrywhitechemmart.com.au/store-api/store",
            headers=headers,
            json=json_data,
        )
        k = r.json()
        hours_info = (
            "".join(k.get("data").get("availability"))
            .replace("MO", "Monday ")
            .replace("TU", " Tuesday ")
            .replace("WE", " Wednesday ")
            .replace("TH", " Thursday ")
            .replace("FR", " Friday ")
            .replace("SA", " Saturday ")
            .replace("SU", " Sunday ")
            or "<MISSING>"
        )
        hours = hours_info.split()
        tmp = []
        if len(hours) == 14:
            for h in hours:
                h = h.replace("noon", "").strip()
                if h.isdigit():
                    h = h[:2] + ":" + h[2:4] + " - " + h[4:6] + ":" + h[6:]
                if h == "XXXXXXXX":
                    h = "Closed"
                tmp.append(h)
        hours_of_operation = " ".join(tmp) or "<MISSING>"

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
            location_type=SgRecord.MISSING,
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
