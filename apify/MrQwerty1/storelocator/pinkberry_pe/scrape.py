from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.google.com/maps/d/u/0/kml?mid=1TX-GBHptKZaj1gPvsz6sJit1L6xoc_So&forcekml=1"
    page_url = "https://www.pinkberry.pe/zonas-de-reparto?rutaExterna=https%3A%2F%2Fwww.google.com%2Fmaps%2Fd%2Fembed%3Fmid%3D1TX-GBHptKZaj1gPvsz6sJit1L6xoc_So%26ll%3D-12.09460324274282%252C-77.03547926265959%26z%3D14"
    r = session.get(api)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//placemark[./name[contains(text(), 'Pinkberry')]]")

    for d in divs:
        location_name = "".join(d.xpath("./name/text()")).strip()
        coords = "".join(d.xpath(".//coordinates/text()")).split(",")
        latitude = coords[0]
        longitude = coords[1]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            country_code="PE",
            locator_domain=locator_domain,
            latitude=latitude,
            longitude=longitude,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.pinkberry.pe/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
