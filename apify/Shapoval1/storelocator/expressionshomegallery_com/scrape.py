from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://expressionshomegallery.com/"
    api_url = "https://expressionshomegallery.com/api/v1/dealers?latitude=34.03054&longitude=-118.38458&radius=10000&pageSize=100&startPage=1&"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["dealers"]
    for j in js:
        slug = j.get("id")
        page_url = f"https://expressionshomegallery.com/Locations/Branch-Locations/Dealer?dealerId={slug}"
        location_name = j.get("name")
        location_type = "Branch"
        street_address = f"{j.get('address1')} {j.get('address2')}".strip()
        state = j.get("state")
        postal = j.get("postalCode")
        country_code = "US"
        city = j.get("city")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("phone")
        hours = j.get("properties").get("hours")
        hours_of_operation = "<MISSING>"
        if hours:
            hours_of_operation = "".join(hours).replace("<br>", " ").strip()
            hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Holiday") != -1:
            hours_of_operation = hours_of_operation.split("Holiday")[0].strip()

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
