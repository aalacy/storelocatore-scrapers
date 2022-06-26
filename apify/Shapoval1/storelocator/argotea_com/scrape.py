from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.argotea.com/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://storelocator.w3apps.co",
        "Connection": "keep-alive",
        "Referer": "https://storelocator.w3apps.co/map.aspx?shop=argotea-2&container=true",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }

    params = (
        ("shop", "argotea-2"),
        ("all", "1"),
    )

    r = session.post(
        "https://storelocator.w3apps.co/get_stores2.aspx",
        headers=headers,
        params=params,
    )
    js = r.json()["location"]
    for j in js:

        page_url = "https://www.argotea.com/apps/store-locator/#locate-a-cafe"
        location_name = j.get("name")
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        street_address = (
            street_address.replace("Global Commons ", "")
            .replace("Fenwick Library", "")
            .replace("Campus Center", "")
            .replace("Folsom Library", "")
            .replace("Red Dragon Outfitters Building", "")
            .replace("Hampden Building", "")
            .strip()
        )
        if street_address.find(",") != -1:
            street_address = street_address.split(",")[0].strip()
        state = j.get("state") or "<MISSING>"
        if state == "<MISSING>":
            continue
        postal = j.get("zip")
        country_code = "USA"
        city = j.get("city")
        latitude = j.get("lat")
        longitude = j.get("long")
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.argotea.com/"
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
