from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api = "https://apis.santaisabel.cl:8443/sisa/json/cms/page-1506.json"
    r = session.get(api, headers=headers)
    js = r.json()["acf"]["localities"]

    for j in js:
        street_address = j.get("address")
        city = j.get("cities")
        state = j.get("regions")
        postal = j.get("ZipCode")
        country_code = "CL"
        location_name = j.get("name")

        try:
            latitude, longitude = str(j.get("geolocation")).split(", ")
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        source = j.get("schedule") or ""
        tree = html.fromstring(source)
        hours_of_operation = " ".join(" ".join(tree.xpath("//text()")).split())
        if "*" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("*")[0].strip()

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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.santaisabel.cl/"
    page_url = "https://www.santaisabel.cl/locales"
    headers = {"x-api-key": "5CIqbUOvJhdpZp4bIE5jpiuFY3kLdq2z"}
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
