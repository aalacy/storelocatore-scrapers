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
    divs = tree.xpath("//div[contains(@class, 'tabs-section')]")

    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        raw_address = "".join(
            d.xpath(".//h3[1]/following-sibling::p[1]/text()")
        ).strip()
        line = raw_address.split(", ")
        line.pop()
        zc = line.pop()
        post = zc.split()[0]
        city = zc.replace(post, "").strip()
        street_address = ", ".join(line)
        latitude, longitude = "".join(d.xpath(".//div/@data-position")).split(", ")
        phone = "".join(d.xpath(".//a[@class='telephone']/text()")).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=post,
            country_code="DE",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.pretamanger.de/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
