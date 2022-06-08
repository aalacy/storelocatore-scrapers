from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='account_box' and .//h1[contains(text(), 'Branch')]]"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//h1/text()"))
        line = d.xpath(".//p/span/text()")
        line = list(filter(None, [li.strip() for li in line]))
        raw_address = ", ".join(line)
        csz = line.pop()
        street_address = ", ".join(line)
        city, sz = csz.split(", ")
        state, postal = sz.split()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            location_type="Branch",
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://fnbfs.com/"
    page_url = "https://fnbfs.com/contact-us/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
