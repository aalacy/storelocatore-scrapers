from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://nyulangone.org/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://nyulangone.org/locations/directory",
        "Proxy-Authorization": "Basic YWNjZXNzX3Rva2VuOjFoMmpscmczNHZrZ3NsYjhob29xZG8zZmpmYWRjaTIyZDRpamc4ZzN1MDAyYzFicWpjNms=",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }

    r = session.get(
        "https://nyulangone.org/locations/directory/all/data.json", headers=headers
    )
    location_types = ["flagshipLocations", "outpatientLocations"]
    for location_type in location_types:
        js = r.json()[f"{location_type}"]
        for j in js:
            slug = j.get("slug")
            page_url = f"https://nyulangone.org/locations/{slug}"
            location_name = j.get("title") or "<MISSING>"
            a = j.get("address")
            ad = "".join(a.get("mapApiText"))

            b = parse_address(International_Parser(), ad)
            street_address = (
                f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = b.state or "<MISSING>"
            postal = b.postcode or "<MISSING>"
            country_code = "US"
            city = b.city or "<MISSING>"
            store_number = j.get("id") or "<MISSING>"
            latitude = a.get("lat") or "<MISSING>"
            longitude = a.get("lng") or "<MISSING>"
            phone = j.get("phone") or "<MISSING>"

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
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        fetch_data(writer)
