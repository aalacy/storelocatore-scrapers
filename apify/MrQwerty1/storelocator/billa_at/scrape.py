from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.billa.at/api/stores"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        street_address = j.get("street")
        city = j.get("city")
        postal = j.get("zip")
        country_code = "AT"
        store_number = j.get("storeId")
        location_type = j.get("brand")
        location_name = j.get("displayName")
        phone = j.get("phone")

        g = j.get("coordinate") or {}
        latitude = g.get("y")
        longitude = g.get("x")

        _tmp = []
        hours = j.get("openingTimes") or []
        for h in hours:
            day = h.get("dayOfWeek")
            inters = h.get("times")
            if inters:
                _tmp.append(f'{day}: {"-".join(inters)}')

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.billa.at/"
    page_url = "https://www.billa.at/maerkte"
    headers = {"correlationid": "5c667c7f-3a34-45f9-a807-f5557fa14c2c-1652280336996"}
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
