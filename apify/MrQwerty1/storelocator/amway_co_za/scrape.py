from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://www.amway.co.za/en/other/site-home/contact-us/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath(
        "//h2[contains(text(), 'Contact')]/following-sibling::*[.//a[contains(text(), 'MAP') or contains(text(), 'Map')]]"
    )
    for d in divs:
        line = d.xpath(".//p//text()")
        line = list(filter(None, [l.strip() for l in line]))
        location_name = line.pop(0)
        latitude, longitude = line.pop().split(",")
        line.pop()
        hours_of_operation = ";".join(line[line.index("Operating Hours") + 1 :])
        line = line[: line.index("Operating Hours")]

        _tmp = []
        phone = SgRecord.MISSING
        for l in line:
            if "Contact" in l or "Fax" in l:
                continue
            if "Tel:" in l:
                phone = l.replace("Tel:", "").strip()
                continue
            _tmp.append(l)

        postal = _tmp.pop()
        state = _tmp.pop()
        city = _tmp.pop()
        street_address = ", ".join(_tmp)
        if street_address.endswith(","):
            street_address = street_address[:-1]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="ZA",
            latitude=latitude,
            longitude=longitude.strip(),
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.amway.co.za/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
