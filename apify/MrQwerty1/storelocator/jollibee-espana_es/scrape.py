import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://www.jollibee-espana.es/findus"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@data-block-json]/@data-block-json"))
    j = json.loads(text)["location"]

    location_name = "".join(tree.xpath("//h1[./following-sibling::h2]/text()")).strip()
    street_address = j.get("addressLine1")
    part = j.get("addressLine2") or ""
    city, state, postal = part.split(", ")
    latitude = j.get("mapLat")
    longitude = j.get("mapLng")

    _tmp = []
    hours = tree.xpath("//p[@class='sqsrte-large']/strong")
    for h in hours:
        day = "".join(h.xpath("./text()")).strip()
        inter = "".join(h.xpath("./following-sibling::text()[1]")).strip()
        _tmp.append(f"{day} {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="ES",
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.jollibee-espana.es/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
