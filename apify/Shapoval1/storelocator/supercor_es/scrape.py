from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://www.supercor.es"
    api_url = "http://www.supercor.es/supercor/cargarAplicacionCentroCercano.do"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="comunidades"]/ul/li/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        city = "".join(d.xpath(".//text()"))
        s_page_url = f"http://www.supercor.es{slug}"
        r = session.get(s_page_url, headers=headers)
        tree = html.fromstring(r.text)
        locations = tree.xpath('//ul[@class="listadotiendas"]/li')
        for l in locations:

            page_u_slug = "".join(l.xpath('.//p[@class="direccion"]/a/@href'))
            page_url = f"http://www.supercor.es{page_u_slug}"
            location_type = "".join(l.xpath('.//p[@class="logo"]/span/text()'))
            location_name = location_type
            street_address = (
                "".join(l.xpath('.//p[@class="direccion"]/text()'))
                .replace("\n", "")
                .replace("-", "")
                .strip()
                or "<MISSING>"
            )
            country_code = "ES"
            phone = (
                "".join(l.xpath('.//p[@class="telefonos"]/text()'))
                .replace("Tel.:", "")
                .replace("\n", "")
                .strip()
            )
            if phone.find("Fax") != -1:
                phone = phone.split("Fax")[0].strip()
            hours_of_operation = (
                "".join(l.xpath('.//p[@class="horario"]/text()'))
                .replace(".", "")
                .strip()
                or "<MISSING>"
            )

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
