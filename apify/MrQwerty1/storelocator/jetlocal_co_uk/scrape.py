from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://api.storerocket.io/api/user/2BkJ1wEpqR/locations?filters=37343"
    r = session.get(api_url)
    js = r.json()["results"]["locations"]

    for j in js:
        street_address = " ".join(
            f"{j.get('address_line_1')} {j.get('address_line_2') or ''}".split()
        )
        city = j.get("state")
        postal = j.get("postcode")
        country_code = j.get("country")
        page_url = j.get("url") or "https://www.jetlocal.co.uk/drivers/locator"
        location_name = j.get("name") or ""
        location_name = " ".join(location_name.split())
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        hours = j.get("hours")
        for k, v in hours.items():
            if not v:
                continue
            _tmp.append(f"{k.capitalize()}: {v}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.jetlocal.co.uk/"
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
