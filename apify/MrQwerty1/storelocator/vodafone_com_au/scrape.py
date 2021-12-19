from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://maps.vodafone.com.au/VHAMap/datafeeds/StoreLocator"
    page_url = "https://www.vodafone.com.au/stores"
    r = session.get(api, headers=headers)
    js = r.json()["stores"]

    for j in js:
        location_name = j.get("tradingName")
        location_type = j.get("type")
        latitude = j.get("lat")
        longitude = j.get("lon")
        phone = j.get("phone")
        store_number = j.get("id")
        street_address = j.get("street")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postcode")

        _tmp = []
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for d in days:
            inter = j.get(f"tradingHours{d}")
            if inter:
                _tmp.append(f"{d}: {inter}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="AU",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            location_type=location_type,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vodafone.com.au/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
