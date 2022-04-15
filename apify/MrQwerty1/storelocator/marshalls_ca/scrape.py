from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://marketingsl.tjx.com/storelocator/GetAllStoresForChain"
    data = {"chain": "93", "lang": "en"}

    r = session.post(api_url, data=data)
    js = r.json()["Stores"]

    for j in js:
        street_address = (
            f"{j.get('Address')} {j.get('Address2') or ''}".replace("<br>", "").strip()
            or "<MISSING>"
        )
        city = j.get("City")
        state = j.get("State")
        postal = j.get("Zip")
        country_code = j.get("Country")
        store_number = j.get("StoreID")
        location_name = j.get("Name")
        phone = j.get("Phone")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        hours_of_operation = j.get("Hours")
        page_url = f"https://www.marshalls.ca/en/storelocator?store={store_number}"
        status = j.get("NewStore")
        if status == "Y" and not hours_of_operation:
            hours_of_operation = "Coming Soon"

        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.marshalls.ca/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
