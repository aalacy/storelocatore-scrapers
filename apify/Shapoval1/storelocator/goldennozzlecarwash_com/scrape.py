from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.goldennozzlecarwash.com"
    api_url = "https://www.goldennozzlecarwash.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//table//tr[./td]")
    for d in div:

        page_url = "https://www.goldennozzlecarwash.com/locations/"
        location_type = "".join(d.xpath("./td[1]/text()"))
        street_address = "".join(d.xpath("./td[3]/a/text()"))
        state = "".join(d.xpath('./preceding::h3[contains(text(), "(")][1]/text()'))
        if state.find("(") != -1:
            state = state.split("(")[0].strip()
        country_code = "US"
        city = "".join(d.xpath("./td[2]/text()"))
        phone = "".join(d.xpath("./td[4]/text()")).strip() or "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath("./td[5]//address/text()")).replace("\n", "").strip()
            or "<MISSING>"
        )
        if hours_of_operation.find(")") != -1:
            hours_of_operation = " ".join(hours_of_operation.split(")")[1:]).strip()
        if hours_of_operation.find("(until further notice :") != -1:
            hours_of_operation = hours_of_operation.split("(until further notice :")[
                1
            ].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=SgRecord.MISSING,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
