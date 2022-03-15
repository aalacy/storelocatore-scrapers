import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.lakeshorelearning.com/api/v1.20.0/int/getAllStores"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        slug = j.get("seoUrl")
        page_url = f"https://www.lakeshorelearning.com{slug}"
        location_name = j.get("name")
        city = j.get("city")
        state = j.get("stateAddress")
        postal = j.get("postalCode")
        adr1 = j.get("address1") or ""
        if adr1[0].isalpha():
            adr1 = ""
        adr2 = j.get("address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        phone = j.get("phoneNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("id")

        source = j.get("openingHours") or "[]"
        hours_of_operation = ";".join(json.loads(source))

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.lakeshorelearning.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
