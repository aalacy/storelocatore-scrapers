from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    page_url = "https://www.pret.ch/en-ch/find-us"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    ad = (
        "".join(
            tree.xpath("//a[contains(@href, 'google')]/preceding-sibling::p[1]/text()")
        )
        .split(",")[0]
        .strip()
    )

    divs = tree.xpath("//div[@class='panel-body tabs-section']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='row']/h3[not(@class)]/text()")
        ).strip()
        part = ", ".join(
            d.xpath(
                ".//div[@class='row']/h3[not(@class)]/following-sibling::p[1]/text()"
            )
        ).strip()
        if "(" in part:
            part = part.split("(")[0].strip()

        street_address = f"{ad} ({part})"
        text = "".join(
            tree.xpath("//script[contains(text(), 'google.maps.LatLng')]/text()")
        )
        latitude, longitude = (
            text.split("google.maps.LatLng(")[1].split("),")[0].split(",")
        )

        _tmp = []
        li = d.xpath(".//h3[@class='opening-title']/following-sibling::p")
        for l in li:
            _tmp.append(" ".join("".join(l.xpath("./text()")).split()))
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city="Zurich",
            country_code="CH",
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.pret.ch/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
