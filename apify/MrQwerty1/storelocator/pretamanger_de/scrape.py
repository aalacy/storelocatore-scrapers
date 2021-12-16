from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    page_url = "https://www.pretamanger.de/en-gb/find-us"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    location_name = "".join(
        tree.xpath("//a[contains(@href, 'google')]/preceding-sibling::h3/text()")
    ).strip()
    street_address = location_name

    text = "".join(
        tree.xpath("//script[contains(text(), 'google.maps.LatLng')]/text()")
    )
    latitude, longitude = text.split("google.maps.LatLng(")[1].split("),")[0].split(",")

    _tmp = []
    li = tree.xpath("//h3[text()='Opening hours']/following-sibling::p")
    for l in li:
        _tmp.append(" ".join("".join(l.xpath("./text()")).split()))
    hours_of_operation = ";".join(_tmp)
    if "closed" in hours_of_operation:
        hours_of_operation = "Temporarily Closed"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city="Berlin",
        country_code="DE",
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.pretamanger.de/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
