import json5
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var markers =')]/text()"))
    text = text.split("var markers =")[1].split("];")[0] + "]"
    js = json5.loads(text)

    for j in js:
        c = j.get("coords") or {}
        latitude = c.get("lat")
        longitude = c.get("lng")

        source = j.get("content") or "<html>"
        d = html.fromstring(source)
        location_name = "".join(d.xpath(".//h6/text()")).strip()
        line = d.xpath("./p/text()")
        line = list(filter(None, [li.strip() for li in line]))
        if len(line) == 1:
            line = line.pop().split(", ")
        pc = line.pop()
        street_address = ", ".join(line)
        postal = pc.split()[0]
        city = pc.replace(postal, "").strip()
        country_code = "BE"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.gulf.be/"
    page_url = "https://www.gulf.be/NL/tankstations.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
