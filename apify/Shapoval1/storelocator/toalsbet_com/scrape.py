from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.toalsbet.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://www.toalsbet.com/shop-locator/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    cookies = {
        "__cf_bm": "ziSNsHMX7V12k4zlMBv7KSwPCAGkvdE1snWTRM6.H2U-1642347912-0-ATqqZ2yIcs7X3qLvDouI5nQIbdsP62vMPa0bzTDaB4TFn86TFFK/Nx5Du0TVG+B+TQjrx9QafIMn1yFlXTfSWcZ9SNE5PZXjaF0wEAYsTk8wptHV6eRTX1y5auU3SJ4Qxo5JoGUJJRwhA2//PIeCi/N5JiCFzMm8MPlDuHmL5JV7RyraBEbEyUPlWxIZjS3Nbw==",
    }
    r = session.get(
        "https://www.toalsbet.com/resources/store_locations.lst",
        headers=headers,
        cookies=cookies,
    )
    js = r.json()["storeLocations"]
    for j in js:

        page_url = "https://www.toalsbet.com/shop-locator/"
        location_name = j.get("name")
        ad = "".join(j.get("address"))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lon")
        phone = j.get("tel") or "<MISSING>"
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
