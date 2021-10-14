from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://uk.loccitane.com/tools/datafeeds/StoresJSON.aspx?task=storelocatorV2"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    js = r.json()["storeList"]["store"]

    for j in js:
        _type = j.get("Type")
        if _type == "NON_OWNED":
            continue

        location_name = j.get("Name")
        slug = j.get("URL")
        page_url = f"https://uk.loccitane.com{slug}"
        street_address = f'{j.get("Address1")} {j.get("Address2") or ""}'.strip()
        city = j.get("City")
        state = j.get("State")
        postal = j.get("ZipCode")
        country_code = j.get("ISO2")
        phone = j.get("Phone")
        g = j.get("coord") or {}
        latitude = g.get("latitude")
        longitude = g.get("longitude")
        store_number = j.get("StoreCode")
        location_type = j.get("Category")

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hours = j.get("RegularOpeningHours") or []
        for h in hours:
            start = h.get("OpenTime")
            end = h.get("CloseTime")
            index = h.get("Day")
            day = days[index]
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://uk.loccitane.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
