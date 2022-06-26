import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.unox.dk/umbraco/surface/MapData/Locations?brandName=UNOX"
    r = session.get(api, headers=headers)
    text = r.text.replace("var mapLocations =", "").strip()
    js = json.loads(text)

    for j in js:
        street_address = j.get("Address")
        city = j.get("City")
        postal = j.get("Zip")
        country_code = "DK"
        store_number = j.get("Id")
        name = j.get("Name") or ""
        location_name = f"Uno-X {name}"
        latitude = str(j.get("Latitude")).replace(",", ".")
        longitude = str(j.get("Longitude")).replace(",", ".")

        _types = []
        if j.get("HasFuel"):
            _types.append("Tankning")
        if j.get("HasWashService"):
            _types.append("Bilvask")

        location_type = ",".join(_types)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            location_type=location_type,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.unox.dk/"
    page_url = "https://www.unox.dk/#findstation"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
