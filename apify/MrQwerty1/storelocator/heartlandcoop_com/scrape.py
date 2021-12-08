from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api_url = "https://heartlandcoop.com/pages/custom.php?id=167"
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    td = tree.xpath("//table[@width='756']//td")

    for t in td:
        isvalid = "".join(t.xpath("./p//text()")).strip()
        if not isvalid:
            continue
        line = t.xpath(".//span//text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[line.index("Heartland Co-op") + 1]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0].strip()
        postal = line.split()[1].strip()
        slug = t.xpath(".//a/@href")
        if slug:
            page_url = f"https://heartlandcoop.com{slug[0]}"
            location_name = "".join(t.xpath(".//a//text()")).strip()
        else:
            location_name = "".join(t.xpath(".//h3//text()")).strip()
            if not location_name:
                p = t.xpath("./p")[0]
                location_name = "".join(p.xpath(".//text()")).strip()
                if not location_name:
                    p = t.xpath("./p")[1]
                    location_name = "".join(p.xpath(".//text()")).strip()
            page_url = SgRecord.MISSING
        phone = (
            t.xpath(".//*[contains(text(), 'Local Phone:')]/text()")[0]
            .replace("Local Phone:", "")
            .strip()
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://heartlandcoop.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
