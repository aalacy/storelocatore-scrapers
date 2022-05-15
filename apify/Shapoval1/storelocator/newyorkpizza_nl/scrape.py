from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.newyorkpizza.nl"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.newyorkpizza.nl",
        "Connection": "keep-alive",
        "Referer": "https://www.newyorkpizza.nl/vestigingen",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = {
        "includeSliceStores": "true",
        "storeIds": "",
    }

    r = session.post(
        "https://www.newyorkpizza.nl/General/GetFilteredStores/",
        headers=headers,
        data=data,
    )
    js = r.json()
    for j in js:

        slug = j.get("details_url")
        page_url = f"https://www.newyorkpizza.nl{slug}"
        location_name = j.get("name")
        street_address = j.get("address_line_1") or "<MISSING>"
        ad = (
            "".join(j.get("address_line_2"))
            .replace("1363BM", "1363 BM")
            .replace("5643KJ", "5643 KJ")
            .replace("7544JB", "7544 JB")
            .replace("5671GX", "5671 GX")
            .replace("4941GE", "4941 GE")
        )
        state = ad.split()[1].strip()
        postal = ad.split()[0].strip()
        country_code = "NL"
        city = " ".join(ad.split()[2:]).strip()
        store_number = j.get("store_id") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        if phone == ".":
            phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("opening_hours")
        tmp = []
        if hours:
            for h in hours:
                day = h.get("key")
                times = h.get("value")
                line = f"{day} {times}"
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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
