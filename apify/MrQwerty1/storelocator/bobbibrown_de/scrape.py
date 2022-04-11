from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.bobbibrown.de/rpc/jsonrpc.tmpl"
    r = session.post(api, headers=headers, data=data, params=params)
    js = r.json()[0]["result"]["value"]["results"].values()

    for j in js:
        adr1 = j.get("ADDRESS") or ""
        adr2 = j.get("ADDRESS2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("CITY")
        state = j.get("STATE_OR_PROVINCE")
        postal = j.get("ZIP_OR_POSTAL")
        country = j.get("COUNTRY") or ""
        if country == "Deutschland":
            cc = "DE"
        elif country == "Österreich":
            cc = "AT"
        else:
            cc = "CH"
        store_number = j.get("DOOR_ID")
        location_type = j.get("STORE_TYPE")
        location_name = j.get("DOORNAME")
        phone = j.get("PHONE1")
        latitude = j.get("LATITUDE")
        longitude = j.get("LONGITUDE")
        hours_of_operation = j.get("STORE_HOURS") or ""
        hours_of_operation = hours_of_operation.replace(
            "Öffnungszeiten<br>", ""
        ).replace("<br>", ";")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=cc,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            location_type=location_type,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.bobbibrown.de/"
    page_url = "https://www.bobbibrown.de/store_locator"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "*/*",
        "Referer": "https://www.bobbibrown.de/store_locator",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.bobbibrown.de",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    params = {
        "dbgmethod": "locator.doorsandevents",
    }

    data = {
        "JSONRPC": '[{"method":"locator.doorsandevents","id":3,"params":[{"fields":"DOOR_ID, DOORNAME, EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE, EVENT_IMAGE, EVENT_FEATURES, EVENT_TIMES, SERVICES, STORE_HOURS, ADDRESS, ADDRESS2, STATE_OR_PROVINCE, CITY, REGION, COUNTRY, ZIP_OR_POSTAL, PHONE1, STORE_TYPE, LONGITUDE, LATITUDE","radius":"5000","country":"Germany","region_id":"2","latitude":52.52000659999999,"longitude":13.404954,"uom":"mile"}]}]',
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
