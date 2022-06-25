from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://www.paris.cl/tiendas-paris.html"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='tablas-abiertas']//tbody/tr")

    for d in divs:
        street_address = "".join(d.xpath("./td[3]/text()")).strip()
        state = "".join(d.xpath("./td[1]/text()")).strip()
        country_code = "CL"
        location_name = "".join(d.xpath("./td[2]/text()")).strip()

        _tmp = []
        lunes = "".join(d.xpath("./td[5]/text()")).strip()
        sabato = "".join(d.xpath("./td[6]/text()")).strip()
        if lunes:
            _tmp.append(f"Lunes a Viernes: {lunes}")
        if sabato:
            _tmp.append(f"Sabado a Domingo: {sabato}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            state=state,
            country_code=country_code,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.paris.cl/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
