import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    jss = tree.xpath("//div/@data-block-json")
    divs = tree.xpath(
        "//div[./p[contains(text(), '@')] or ./h3/strong[contains(text(), '@')]]"
    )

    for js, d in zip(jss, divs):
        j = json.loads(js)["location"]

        location_name = "".join(d.xpath(".//h2//text()")).strip()
        line = d.xpath(".//h3//text()")
        line = list(filter(None, [li.strip() for li in line]))
        if "@" in line[-1]:
            line.pop()

        phone = SgRecord.MISSING
        if len(line) > 1:
            phone = line.pop()
        street_address = ", ".join(line)

        adr = j.get("addressLine2") or ""
        city, state, postal = SgRecord.MISSING, SgRecord.MISSING, SgRecord.MISSING
        if adr:
            a = adr.split(", ")
            if len(a) == 3:
                city, state, postal = a
            elif len(a) == 2:
                city, state = a
                postal = SgRecord.MISSING
            elif len(a) == 1:
                city = a.pop()

        if city == SgRecord.MISSING and "LAS" in location_name:
            city = "Madrid"
        if city == SgRecord.MISSING:
            city = location_name.split("-")[-1].strip()

        country_code = "ES"
        latitude = j.get("markerLat")
        longitude = j.get("markerLng")

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
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.alohapoke.es/"
    page_url = "https://www.alohapoke.es/localizaciones"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
