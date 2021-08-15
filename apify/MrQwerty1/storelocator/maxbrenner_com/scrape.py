from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    page_url = "https://maxbrenner.com/pages/branches"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@id, 'map-info-home-map-')]")

    for d in divs:
        location_name = "".join(d.xpath("./preceding-sibling::a[1]/h3/text()")).strip()
        line = []

        text = d.xpath(".//div[@class='home-map__text rte']/p//text()")
        for t in text:
            if not t.strip() or ":" in t or "@" in t:
                continue
            line.append(t.strip())

        phone = line.pop()
        raw = line.pop()
        line = raw.split(", ")
        street_address = line.pop(0)
        city = line.pop(0)
        line = line.pop(0)
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        hours_of_operation = ";".join(
            d.xpath(".//div[@class='home-map__sub-text u-small rte']/p/text()")
        )
        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://maxbrenner.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
