from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ambev.com.br/"
    page_url = "https://www.ambev.com.br/visitas/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="accordion__content"]')
    for d in div:

        location_name = "".join(d.xpath("./a/text()")).replace("\n", "").strip()
        info = " ".join(d.xpath(".//p//text()")).replace("\n", "").strip()
        ad = d.xpath('.//p[.//*[text()="Mais informações"]]/text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        phone = "<MISSING>"
        for i in ad:
            if "Tel" in i:
                phone = (
                    str(i).replace("Tel", "").replace(":", "").replace(".", "").strip()
                )
        if phone.find("|") != -1:
            phone = phone.split("|")[0].strip()
        adr = " ".join(ad).replace("|", "").strip()
        if adr.find(f"{phone}") != -1:
            adr = adr.split(f"{phone}")[1].strip()
        adr = (
            adr.replace("Endereço:", "")
            .replace("Grupos de até 30 pessoas", "")
            .replace("Grupos de até 20 pessoas", "")
            .replace("Grupos de até 25 pessoas", "")
            .strip()
        )
        if adr.find("(Domingo)") != -1:
            adr = adr.split("(Domingo)")[1].strip()
        b = parse_address(International_Parser(), adr)
        street_address = (
            f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )

        postal = b.postcode or "<MISSING>"
        postal = str(postal).replace("CEP", "").strip()
        country_code = "BR"
        state = location_name.split("(")[1].split("-")[1].split(")")[0].strip()
        city = location_name.split("(")[1].split("-")[0].strip()
        hours_of_operation = "<MISSING>"
        if info.find("Horários de funcionamento") != -1:
            hours_of_operation = info.split("Horários de funcionamento")[1].strip()
        if hours_of_operation.find("Mais informações") != -1:
            hours_of_operation = hours_of_operation.split("Mais informações")[0].strip()
        if hours_of_operation.find("Preço") != -1:
            hours_of_operation = hours_of_operation.split("Preço")[0].strip()
        if hours_of_operation.find("As visitas") != -1:
            hours_of_operation = hours_of_operation.split("As visitas")[0].strip()
        hours_of_operation = (
            hours_of_operation.replace("(para grupos de estudantes, empresas, etc)", "")
            .replace("(disponibilidade mensal)", "")
            .replace("(chegar com 20 minutos de antecedência)", "")
            .replace("*", "")
            .replace("Grupos de até 30 pessoas", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
