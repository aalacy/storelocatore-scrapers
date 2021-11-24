from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.vodafone.pt/bin/mvc.do/sites/store/getStores?"
    page_url = "https://www.vodafone.pt/lojas.html"
    r = session.get(api, headers=headers)

    for j in r.json():
        location_name = j.get("name")
        latitude = j.get("lat")
        longitude = j.get("lon")
        phone = j.get("whatsappNumber")
        a = j.get("address") or {}
        num = a.get("streetNr") or ""
        street = a.get("streetName") or ""
        street_address = f"{num} {street}"
        city = a.get("city")
        state = a.get("stateOrProvince")
        postal = a.get("postcode")
        hours = j.get("hours") or ""
        hours_of_operation = " ".join(hours.split())

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="PT",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vodafone.pt/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
