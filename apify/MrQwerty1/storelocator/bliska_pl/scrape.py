import csv
from io import BytesIO
from zipfile import ZipFile
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.bliska.pl/_layouts/f2hBliska/zip/Garmin_Bliska.zip"
    r = session.get(api, headers=headers)
    zipfile = ZipFile(BytesIO(r.content))
    path = zipfile.namelist().pop()
    with zipfile.open(path) as q:
        source = q.read().decode(encoding="cp1250")
        rows = csv.DictReader(source.splitlines())

        for j in rows:
            raw_address = j.get("addr") or ""
            city, street_address = raw_address.split(", ")
            country_code = "PL"
            location_name = j.get("name")
            latitude = j.get("geo_y")
            longitude = j.get("geo_x")

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.bliska.pl/"
    page_url = "https://www.bliska.pl/PL/ZnajdzStacje/Strony/default.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
