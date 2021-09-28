from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tootsies.ca/"
    api_url = "https://cdn.shopify.com/s/files/1/0427/8727/4906/t/20/assets/sca.storelocatordata.json?v=1629305526&_=1632861860679"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.tootsies.ca/pages/store-locator"
        location_name = "".join(j.get("name"))
        location_type = "<MISSING>"
        street_address = j.get("address")
        state = j.get("state")
        postal = j.get("postal")
        country_code = j.get("country")
        city = j.get("city")
        store_number = "<MISSING>"
        if location_name.find("#") != -1:
            store_number = location_name.split("#")[1].strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        hours_of_operation = (
            "".join(j.get("schedule")).replace("\r", "").replace("<br>", " ").strip()
        )
        if hours_of_operation.find("pick up") != -1:
            hours_of_operation = hours_of_operation.split("ick up from")[1].strip()

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
