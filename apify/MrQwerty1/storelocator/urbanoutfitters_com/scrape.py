from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.urbanoutfitters.com/api/misl/v1/stores/search?&urbn_key=937e0cfc7d4749d6bb1ad0ac64fce4d5&brandId=51|01"
    r = session.get(api, headers=headers)
    js = r.json()["results"]

    for j in js:
        try:
            location_name = j["addresses"]["marketing"]["name"] or ""
        except KeyError:
            location_name = j.get("storeName") or ""

        try:
            m = j["addresses"]["marketing"] or {}
            street_address = m.get("addressLineOne")
            phone = m.get("phoneNumber")
            country_code = j["addresses"]["iso2"]["country"] or j.get("country")
        except:
            street_address = j.get("addressLineOne")
            phone = j.get("storePhoneNumber") or ""
            if "?" in phone:
                phone = SgRecord.MISSING
            country_code = j.get("country")

        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        store_number = j.get("storeNumber")
        slug = j.get("slug")
        page_url = SgRecord.MISSING
        if slug:
            page_url = f"https://www.urbanoutfitters.com/stores/{slug}"
        loc = j.get("loc") or [SgRecord.MISSING, SgRecord.MISSING]
        latitude = loc[1]
        longitude = loc[0]

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
        hours = j.get("hours")
        for d, h in zip(days, hours.values()):
            start = h.get("open").lower()
            close = h.get("close").lower()
            if start == "closed" or close == "closed":
                _tmp.append(f"{d} CLOSED")
            else:
                _tmp.append(f"{d} {start} - {close}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.urbanoutfitters.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
