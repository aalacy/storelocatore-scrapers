import re
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()

    return street_address


def fetch_data(sgw: SgWriter):
    api = "https://sea.sunglasshut.com/api/content/render/false/limit/9999/type/json/query/+contentType:SghStoreLocator%20+languageId:9%20+deleted:false%20+working:true/orderby/modDate%20desc"

    r = session.get(api)
    js = r.json()["contentlets"]

    for j in js:
        location_name = j.get("name")
        slug = j.get("seoUrl") or "/"
        page_url = f"https://sea.sunglasshut.com/sg/{slug}"
        raw_address = j.get("address") or ""
        try:
            postal = re.findall(r"\d{5,}", raw_address).pop()
        except:
            postal = SgRecord.MISSING
        street_address = get_international(raw_address)
        if len(street_address) < 5:
            street_address = raw_address.split(",")[0].strip()
        if postal in street_address:
            street_address = raw_address.split(f", {postal}")[0].strip()
        city = j.get("city")
        country_code = j.get("state")
        phone = j.get("phone")
        latitude = j.get("geographicCoordinatesLatitude")
        longitude = j.get("geographicCoordinatesLongitude")
        if latitude == 0:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in days:
            _tmp.append(f"{day}: {j.get(day)}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            location_name=location_name,
            page_url=page_url,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://sea.sunglasshut.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
