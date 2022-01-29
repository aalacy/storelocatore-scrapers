from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.skopes.co.uk/store-locator/ajax/stores"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("name")
        street_address = f'{j.get("address")} {j.get("address_2") or ""}'.strip()
        city = j.get("city")
        postal = j.get("postcode")
        country = j.get("country")

        phone = j.get("phone") or ""
        if "e" in phone:
            phone = phone.split("e")[0].strip()
        if "o" in phone:
            phone = phone.split("o")[0].strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("stockist_id")

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
    locator_domain = "https://www.skopes.co.uk/"
    page_url = "https://www.skopes.co.uk/store-locator/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
