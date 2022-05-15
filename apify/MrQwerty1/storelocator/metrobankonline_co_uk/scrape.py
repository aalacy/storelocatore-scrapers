from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.metrobankonline.co.uk/api/location/getlocationlist/"
    r = session.get(api, headers=headers)
    js = r.json()["locations"]

    for j in js:
        slug = j.get("locationLink") or ""
        page_url = f"https://www.metrobankonline.co.uk{slug}"

        i = j.get("cardInfo")
        location_name = i.get("name")

        a = i.get("address") or ["", "", ""]
        postal = a.pop()
        if len(a) == 2:
            street_address = a.pop(0)
            city = a.pop(0)
        else:
            t = a[1].lower()
            if "centre" in t or a[1][0].isdigit() or "house" in t:
                street_address = " ".join(a[:2])
                city = a.pop()
            else:
                street_address = a.pop(0)
                city = a.pop(0)

        opt = i.get("optionalFields") or []
        for o in opt:
            phone = o.get("Telephone ")
            if phone:
                break
        else:
            phone = SgRecord.MISSING

        c = j.get("coords") or {}
        latitude = c.get("lat")
        longitude = c.get("lng")
        location_type = j.get("type")
        store_number = j.get("locationId")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            location_type=location_type,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.metrobankonline.co.uk/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
