from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api = "https://www.q8.it/geolocalizzatore/pv/all"
    r = session.get(api, headers=headers)
    countries = ("BE", "LU", "NL", "FR", "ES")
    js = r.json()

    for j in js:
        location_name = j.get("localita")
        street_address = j.get("indirizzo") or ""
        street_address = street_address.upper().replace(">", "-").strip()
        city = j.get("localita")
        postal = j.get("cap")
        phone = j.get("telefono")
        latitude = j.get("latitudine") or ""
        longitude = j.get("longitudine") or ""
        if str(latitude) == "0.0":
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        store_number = j.get("codice") or ""
        for c in countries:
            if c in store_number:
                country = c
                break
        else:
            country = "IT"

        if country == "BE":
            continue

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.q8.it/"
    page_url = "https://www.q8.it/en_GB/distributori-q8"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
