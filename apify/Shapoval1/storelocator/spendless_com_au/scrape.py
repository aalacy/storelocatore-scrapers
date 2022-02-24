from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.spendless.com.au/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.spendless.com.au/stores",
        "X-NewRelic-ID": "VwIHVFNTGwsJXVhSDgEF",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.spendless.com.au",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    data = {
        "key": "AIzaSyBBmCV6MpgFqu7dq9ummJrwbXsD5OeCOdU",
        "components[country]": "AU",
        "radius": "5000000",
        "units": "km",
        "page": "0",
        "address": "2612",
    }

    r = session.post(
        "https://www.spendless.com.au/stockists/index/search/",
        headers=headers,
        data=data,
    )
    js = r.json()["results"]["results"]
    for j in js:

        page_url = "https://www.spendless.com.au/stores"
        location_name = j.get("name") or "<MISSING>"
        ad = f"{j.get('street')} {j.get('street2')}".replace("None", "").strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = j.get("state") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = "AU"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = (
            "".join(j.get("opening_hours"))
            .replace("\n", " ")
            .replace("\r", " ")
            .strip()
            or "<MISSING>"
        )

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
