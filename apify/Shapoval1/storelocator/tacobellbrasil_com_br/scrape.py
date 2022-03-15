from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tacobellbrasil.com.br/"
    api_url = "https://www.tacobellbrasil.com.br/lojas"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="span4 ba-grid-column-wrapper"]')
    for d in div:

        page_url = "https://www.tacobellbrasil.com.br/lojas"
        location_name = " ".join(d.xpath(".//h5/text()"))
        if not location_name:
            continue
        street_address = "".join(d.xpath(".//h5/following-sibling::p[1]/text()[1]"))
        ad = (
            "".join(d.xpath(".//h5/following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        country_code = "Brazil"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
