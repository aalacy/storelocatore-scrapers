from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://localistico-production.s3.eu-west-1.amazonaws.com/exports/locations/json/business-694cbc6c-9274-48b0-b509-f989f7febed2-locations-data-20211117085037.json"
    page_url = "https://www.vodafone.nl/support/contact/vind-een-winkel"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("location_name")
        store_number = j.get("location_code")
        latitude = j.get("location_lat")
        longitude = j.get("location_lng")
        phone = j.get("phone")
        street_address = f'{j.get("street_address")} {j.get("street_address_second_line") or ""}'.strip()
        city = j.get("locality")
        state = j.get("region")
        postal = j.get("postcode")
        hours = j.get("hours") or ""

        _tmp = []
        hours = hours.split("|")
        for h in hours:
            if not h.endswith(":"):
                _tmp.append(h)

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="NL",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vodafone.nl/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
