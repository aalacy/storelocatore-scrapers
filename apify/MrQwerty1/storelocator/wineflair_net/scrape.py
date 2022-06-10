from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://wineflair.net/stores/xml.xml"
    r = session.get(api)
    tree = html.fromstring(r.content)

    divs = tree.xpath("//marker")
    for d in divs:
        location_name = "".join(d.xpath("./@name"))
        page_url = "".join(d.xpath("./@web"))
        adr1 = "".join(d.xpath("./@address"))
        adr2 = "".join(d.xpath("./@address2")) or ""
        street_address = f"{adr1} {adr2}".strip()
        phone = "".join(d.xpath("./@phone"))
        city = "".join(d.xpath("./@city"))
        postal = "".join(d.xpath("./@postal"))
        latitude = "".join(d.xpath("./@lat"))
        longitude = "".join(d.xpath("./@lng"))

        _tmp = []
        for i in range(1, 4):
            t = "".join(d.xpath(f"./@hours{i}"))
            if t:
                _tmp.append(t)
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://wineflair.net/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
